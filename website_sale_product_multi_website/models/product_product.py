# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def open_website_url(self):
        self.ensure_one()
        if not self.product_tmpl_id.website_ids:
            return super().open_website_url()
        # The standard variant action replaces the template action URL.
        return self.product_tmpl_id._get_multi_website_action(self.website_url)
