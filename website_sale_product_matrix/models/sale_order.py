# Copyright 2026 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cart_find_product_line(
        self, product_id, uom_id, linked_line_id=False, **kwargs
    ):
        """Return the line of the variant set from the product matrix.

        The matrix sets the quantity of the line of each variant, as in the product
        page, even if it has custom attribute values, which aren't matched here.
        """
        line_id = self.env.context.get("website_sale_product_matrix_line_id")
        line = self.order_line.filtered(lambda line: line.id == line_id)
        if line and line.product_id.id == product_id and not linked_line_id:
            return line
        return super()._cart_find_product_line(
            product_id, uom_id, linked_line_id=linked_line_id, **kwargs
        )
