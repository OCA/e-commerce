from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cart_update(self, product_id, line_id=None, add_qty=0, set_qty=0, **kwargs):
        product = self.env["product.product"].browse(product_id)
        if not product._show_quick_add_accesory_assortments() and not (
            add_qty == 0 or (not add_qty and set_qty == 0)
        ):
            raise UserError(
                _("It cannot be added to the cart because the product is restricted.")
            )
        return super()._cart_update(
            product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            **kwargs,
        )
