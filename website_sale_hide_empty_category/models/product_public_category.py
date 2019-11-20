# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models
from odoo.addons.website_sale.controllers.main import WebsiteSale


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    def _compute_is_empty(self):
        websiteSale = WebsiteSale()
        for category in self:
            domain = websiteSale._get_search_domain(search=None, category=category.id, attrib_values=None)
            count = self.env['product.template'].search_count(domain)
            category.is_empty = False if count > 0 else True

    is_empty = fields.Boolean('Is Empty', compute="_compute_is_empty")
