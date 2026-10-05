# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models
from odoo.tools import float_round


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _format_matrix_free_qty(self, qty):
        """Format the matrix free quantity for display."""
        return int(qty) if float(qty).is_integer() else qty

    def _get_template_matrix(self, **kwargs):
        # The base method prepares the data for each matrix cell. Stock is computed
        # later per cell, so include it here to compute all quantities in batch.
        matrix = super()._get_template_matrix(**kwargs)
        website = self.env["website"].get_current_website()
        variants = self.sudo().product_variant_ids.with_context(
            warehouse=website.warehouse_id.id,
            # Support website_sale_stock_available when installed.
            website_sale_stock_available=True,
        )
        free_qty_by_combination = {
            frozenset(variant.product_template_attribute_value_ids.ids): float_round(
                variant.free_qty,
                precision_digits=0,
                rounding_method="DOWN",
            )
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
        self, product_or_template, quantity, uom, date, website
    ):
        res = super()._get_additionnal_combination_info(
            product_or_template, quantity, uom, date, website
        )
        # Use template-wide stock for the matrix availability message.
        if (
            self.env.context.get("website_sale_stock_get_quantity")
            and self.product_add_mode == "matrix"
            and self.is_storable
            and product_or_template.is_product_variant
        ):
            total_qty = sum(
                variant.uom_id._compute_quantity(
                    website._get_product_available_qty(variant),
                    to_unit=uom,
                    round=False,
                )
                for variant in self.sudo().product_variant_ids
            )
            res["free_qty"] = float_round(
                total_qty, precision_digits=0, rounding_method="DOWN"
            )
        return res
