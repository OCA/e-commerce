from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        """Force quantity on product from what is defined in product.template"""
        # Need to call super first to ensure correct default mechanism
        res = super()._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)
        # Do nothing if we are removing the product (qty=0)
        if res["quantity"] > 0 and product_id:
            product = self.env["product.product"].browse(product_id)
            if product.website_sale_force_qty:
                new_res = super()._cart_update(product_id, line_id, add_qty=0, set_qty=product.website_sale_force_qty, **kwargs)
                res.update(new_res)
        return res
