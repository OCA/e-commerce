# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import http

from odoo.addons.website_sale.controllers.main import WebsiteSale


class ProductAttribute(WebsiteSale):
    @http.route()
    def shop(self, page=0, category=None, search="", ppg=False, **post):
        response = super().shop(
            page=page, category=category, search=search, ppg=ppg, **post
        )
        attributes = response.qcontext.get("attributes")
        if attributes:
            response.qcontext["attributes"] = attributes.filtered("website_published")
        return response
