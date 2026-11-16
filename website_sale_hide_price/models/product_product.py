# Copyright 2024 Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _is_add_to_cart_allowed(self) -> bool:
        self.ensure_one()
        website = self.env.website
        website_show_price = website.website_show_price if website else True
        if self.product_tmpl_id.website_hide_price or not website_show_price:
            return False
        return super()._is_add_to_cart_allowed()
