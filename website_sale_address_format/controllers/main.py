# Copyright 2020 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    @http.route()
    def shop_country_info(self, country, address_type, **kw):
        res = super().shop_country_info(country, address_type, **kw)
        if country.online_address_format:
            res["fields"] = country.get_online_address_fields()
        return res
