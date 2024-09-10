# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import SUPERUSER_ID, http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class CheckoutSkipPaymentWebsite(WebsiteSale):
    def _get_shop_payment_values(self, order, **kwargs):
        values = super()._get_shop_payment_values(order, **kwargs)
        partner = values.get("partner")
        if partner.skip_website_checkout_payment:
            values["hide_payment_button"] = True
        return values

    @http.route()
    def shop_payment_confirmation(self, **post):
        """When we skip the payment, we'll just confirm the order and send the proper
        confirmation message"""
        order_id = request.session.get("sale_last_order_id")
        if not request.website.checkout_skip_payment or not order_id:
            return super().shop_payment_confirmation(**post)
        order = request.env["sale.order"].sudo().browse(order_id)
        try:
            order.with_context(send_email=True, mark_so_as_sent=True).with_user(
                SUPERUSER_ID
            ).action_confirm()
        except Exception:
            return request.render(
                "website_sale_checkout_skip_payment.confirmation_order_error"
            )
        request.website.sale_reset()
        values = self._prepare_shop_payment_confirmation_values(order)
        return request.render("website_sale.confirmation", values)
