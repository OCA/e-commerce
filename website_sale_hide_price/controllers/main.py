# Copyright 2026 FactorLibre - Sushan Voong
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    def checkout_redirection(self, order):
        if request.website and not request.website.website_show_price:
            return request.redirect("/shop")
        return super().checkout_redirection(order=order)

    @http.route()
    def cart(self, **post):
        if request.website and not request.website.website_show_price:
            return request.redirect("/shop")
        return super().cart(**post)

    @http.route()
    def cart_update(self, *args, **kw):
        if request.website and not request.website.website_show_price:
            return request.redirect("/shop")
        return super().cart_update(*args, **kw)
