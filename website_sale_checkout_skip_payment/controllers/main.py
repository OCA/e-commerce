# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.http import request, route

from odoo.addons.website_sale.controllers.main import WebsiteSale


class CheckoutSkipPaymentWebsite(WebsiteSale):
    @route()
    def shop_payment_get_status(self, sale_order_id, **post):
        """When skip payment step, the transaction not exists so only render the waiting
        message in ajax json call"""
        if not request.website.checkout_skip_payment:
            return super().shop_payment_get_status(sale_order_id, **post)
        return {
            "recall": True,
            "message": request.website._render(
                "website_sale_checkout_skip_payment.order_state_message"
            ),
        }

    @route()
    def shop_payment_confirmation(self, **post):
        """When we skip the payment, we'll just confirm the order and send the proper
        confirmation message"""
        order_id = request.session.get("sale_last_order_id")
        if not request.website.checkout_skip_payment or not order_id:
            return super().shop_payment_confirmation(**post)
        order = request.env["sale.order"].sudo().browse(order_id)
        try:
            order.with_context(mark_so_as_sent=True)._send_order_confirmation_mail()
        except Exception:
            return request.render(
                "website_sale_checkout_skip_payment.confirmation_order_error"
            )
        # This could not finish (e.g.: sale_financial_risk exceeded)
        order.action_confirm()
        request.website.sale_reset()
        return request.render(
            "website_sale.confirmation",
            {"order": order, "order_tracking_info": self.order_2_return_dict(order)},
        )
