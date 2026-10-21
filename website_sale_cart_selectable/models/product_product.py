# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _is_add_to_cart_allowed(self):
        self.ensure_one()
        if not self.website_btn_addtocart_published:
            return False
        return super()._is_add_to_cart_allowed()
