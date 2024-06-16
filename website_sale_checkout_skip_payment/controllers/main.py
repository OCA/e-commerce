# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.http import request

from odoo.addons.payment.controllers.portal import PaymentPortal
from odoo.addons.website_sale.controllers.main import WebsiteSale


class CheckoutSkipPaymentWebsite(WebsiteSale):

    def _get_shop_payment_values(self, order, **kwargs):
        res = super()._get_shop_payment_values(order, **kwargs)
        if order.website_id.checkout_skip_payment:
            res['submit_button_label'] = "Confirm"
            res["hide_payment_button"] = True
        return res


class CheckoutSkipPayment(PaymentPortal):
    @http.route()
    def payment_confirm(self, tx_id, access_token, **kwargs):
        if not request.website.checkout_skip_payment:
            return super().payment_confirm(tx_id, access_token, **kwargs)
        order = (
            request.env["sale.order"]
            .sudo()
            .browse(request.session.get("sale_last_order_id"))
        )
        order.action_confirm()
        try:
            order._send_order_confirmation_mail()
        except Exception:
            return request.render(
                "website_sale_checkout_skip_payment.confirmation_order_error"
            )
        request.website.sale_reset()
        return request.render("website_sale.confirmation", {"order": order})
