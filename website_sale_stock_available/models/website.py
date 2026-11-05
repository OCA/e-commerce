# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _get_product_available_qty(self, product, **kwargs):
        return super()._get_product_available_qty(
            product.with_context(website_sale_stock_available=True), **kwargs
        )
