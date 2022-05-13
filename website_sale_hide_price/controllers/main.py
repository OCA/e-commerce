# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    def _get_products_recently_viewed(self):
        """When the prices are hidden globally we should force to hide everyone"""
        res = super()._get_products_recently_viewed()
        if request.website.website_show_price:
            return res
        for product in res.get("products", []):
            product["website_hide_price"] = True
        return res
