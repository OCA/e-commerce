# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    @http.route()
    def country_infos(self, country, mode, **kw):
        res = super(WebsiteSale, self).country_infos(country, mode, **kw)
        if country.online_address_format:
            res["fields"] = country.get_online_address_fields()
        return res
