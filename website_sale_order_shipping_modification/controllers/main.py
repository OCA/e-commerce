# Copyright 2025 Tecnativa - Pilar Vargas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleOrderShippingModification(WebsiteSale):
    def checkout_check_address(self, order):
        portal_order_id = request.session.get("portal_order_id", False)
        portal_access_token = request.session.get("portal_access_token", False)
        sale_order_id = request.session.get("sale_order_id", False)
        if portal_order_id and portal_access_token and sale_order_id:
            return
        return super().checkout_check_address(order=order)

    def checkout_redirection(self, order):
        portal_order_id = request.session.get("portal_order_id", False)
        portal_access_token = request.session.get("portal_access_token", False)
        sale_order_id = request.session.get("sale_order_id", False)
        if portal_order_id and portal_access_token and sale_order_id:
            return None
        return super().checkout_redirection(order=order)

    @http.route()
    def address(self, **kw):
        portal_order_id = request.session.get("portal_order_id", False)
        portal_access_token = request.session.get("portal_access_token", False)
        res = super().address(**kw)
        if (
            portal_order_id
            and portal_access_token
            and "submitted" in kw
            and request.httprequest.method == "POST"
        ):
            location = res.headers.get("Location")
            if location and location.endswith("/shop/confirm_order"):
                return request.redirect("/shop/checkout")
        return res

    @http.route()
    def checkout(self, **post):
        portal_order_id = post.get("portal_order_id", False)
        access_token = post.get("access_token", False)
        if portal_order_id and access_token:
            request.session["portal_order_id"] = int(portal_order_id)
            request.session["portal_access_token"] = access_token
            request.session["sale_order_id"] = int(portal_order_id)
        return super().checkout(**post)
