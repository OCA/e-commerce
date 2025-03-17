from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _show_quick_add_accesory_assortments(self):
        res = self._website_show_quick_add()
        if not res:
            return res
        return not bool(
            self.env["product.template"].get_product_assortment_restriction_info(
                self.ids
            )
        )
