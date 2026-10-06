# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_template_matrix(self, **kwargs):
        # The base method prepares the data for each matrix cell. Stock is computed
        # later per cell, so include it here to compute all quantities in batch.
        matrix = super()._get_template_matrix(**kwargs)
        website = self.env["website"].get_current_website()
        variants = self.sudo().product_variant_ids.with_context(
            warehouse=website._get_warehouse_available(),
            # Support website_sale_stock_available when installed.
            website_sale_stock_available=True,
        )
        free_qty_by_combination = {
            frozenset(
                variant.product_template_attribute_value_ids.ids
            ): variant.free_qty
            for variant in variants
        }
        ptav_model = self.env["product.template.attribute.value"]
        for row in matrix["matrix"]:
            for cell in row[1:]:
                combination = ptav_model.browse(cell["ptav_ids"])
                cell["free_qty"] = free_qty_by_combination.get(
                    frozenset(combination._without_no_variant_attributes().ids),
                    0.0,
                )
        return matrix

    def _get_additionnal_combination_info(
        self, product_or_template, quantity, date, website
    ):
        res = super()._get_additionnal_combination_info(
            product_or_template, quantity, date, website
        )
        # For products sold through the variant matrix the variant selector is
        # hidden, so the page-level availability message stays frozen on the first
        # variant and wrongly shows "out of stock" when only the first size/color
        # is depleted. The message must reflect the whole template instead: if ANY
        # variant has stock the product isn't out of stock.
        if (
            self.product_add_mode == "matrix"
            and self.type == "product"
            and product_or_template.is_product_variant
        ):
            res["free_qty"] = sum(
                website._get_product_available_qty(variant)
                for variant in self.sudo().product_variant_ids
            )
        return res
