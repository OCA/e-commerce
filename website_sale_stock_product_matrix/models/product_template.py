# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

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
        # variant has stock the product isn't out of stock. The matrix grid cells
        # still need the per-variant quantity, so those calls are flagged with the
        # `product_matrix_cell` context and left untouched.
        if (
            self.product_add_mode == "matrix"
            and self.type == "product"
            and product_or_template.is_product_variant
            and not self.env.context.get("product_matrix_cell")
        ):
            res["free_qty"] = sum(
                website._get_product_available_qty(variant)
                for variant in self.sudo().product_variant_ids
            )
        return res
