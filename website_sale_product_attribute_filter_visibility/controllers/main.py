# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http


class ProductAttribute(WebsiteSale):

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        response = super(ProductAttribute, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post)
        response.qcontext['attributes'] = (
            response.qcontext['attributes'].filtered('website_published'))
        return response
