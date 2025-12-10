# Copyright 2025 Tecnativa - Pilar Vargas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleOrderShippingModification(WebsiteSale):
    def _check_cart(self, order_sudo):
        portal_order_id = request.session.get("portal_order_id", False)
        portal_access_token = request.session.get("portal_access_token", False)
        sale_order_id = request.session.get("sale_order_id", False)
        if portal_order_id and portal_access_token and sale_order_id:
            return
        return super()._check_cart(order_sudo=order_sudo)

    @http.route()
    def shop_address(
        self,
        partner_id=None,
        address_type="billing",
        use_delivery_as_billing=None,
        **query_params,
    ):
        portal_order_id = request.session.get("portal_order_id", False)
        portal_access_token = request.session.get("portal_access_token", False)
        res = super().shop_address(
            partner_id=partner_id,
            address_type=address_type,
            use_delivery_as_billing=use_delivery_as_billing,
            **query_params,
        )
        if (
            portal_order_id
            and portal_access_token
            and "submitted" in query_params
            and request.httprequest.method == "POST"
        ):
            location = res.headers.get("Location")
            if location and location.endswith("/shop/confirm_order"):
                return request.redirect("/shop/checkout")
        return res

    @http.route()
    def shop_checkout(self, try_skip_step=None, **query_params):
        portal_order_id = query_params.get("portal_order_id", False)
        access_token = query_params.get("access_token", False)
        if portal_order_id and access_token:
            request.session["portal_order_id"] = int(portal_order_id)
            request.session["portal_access_token"] = access_token
            request.session["sale_order_id"] = int(portal_order_id)
        return super().shop_checkout(try_skip_step=try_skip_step, **query_params)
