# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models
from odoo.tools import float_round


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _format_matrix_free_qty(self, qty):
        """Format a matrix cell's free quantity for display.

        Mirrors `SaleOrder._verify_updated_quantity()`'s own `format_qty()` in
        `website_sale_stock`: avoid a spurious trailing ``.0`` for whole
        numbers, while still showing genuinely fractional quantities as-is.
        """
        return int(qty) if float(qty).is_integer() else qty

    def _get_additionnal_combination_info(
        self, product_or_template, quantity, uom, date, website
    ):
        res = super()._get_additionnal_combination_info(
            product_or_template, quantity, uom, date, website
        )
        # For products sold through the variant matrix the variant selector is
        # hidden, so the page-level availability message stays frozen on the first
        # variant and wrongly shows "out of stock" when only the first size/color
        # is depleted. The message must reflect the whole template instead: if ANY
        # variant has stock the product isn't out of stock. The matrix grid cells
        # still need the per-variant quantity, so those calls are flagged with the
        # `product_matrix_cell` context and left untouched.
        if (
            self.env.context.get("website_sale_stock_get_quantity")
            and self.product_add_mode == "matrix"
            and self.is_storable
            and product_or_template.is_product_variant
            and not self.env.context.get("product_matrix_cell")
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
