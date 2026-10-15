# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import http
from odoo.http import request

from odoo.addons.website_sale_checkout_skip_payment.controllers.main import (
    CheckoutSkipPaymentWebsite,
)

_logger = logging.getLogger(__name__)


class CheckoutSkipPaymentQuotation(CheckoutSkipPaymentWebsite):
    @http.route()
    def shop_payment_confirmation(self, **post):
        """When skipping payment, keep the order as a quotation (do not confirm)
        and notify the customer with the dedicated quotation email template.
        """
        order_id = request.session.get("sale_last_order_id")
        if not request.website.checkout_skip_payment or not order_id:
            return super().shop_payment_confirmation(**post)
        order = request.env["sale.order"].sudo().browse(order_id)
        template = request.env.ref(
            "website_sale_checkout_skip_payment_quotation."
            "mail_template_sale_quotation_skip_payment",
            raise_if_not_found=False,
        )
        if not template:
            _logger.warning(
                "Quotation skip-payment mail template not found; "
                "falling back to parent behaviour."
            )
            return super().shop_payment_confirmation(**post)
        try:
            # Note: we deliberately do NOT pass ``mark_so_as_sent=True`` here so the
            # order stays in ``draft`` (Quotation) state. The parent module passes
            # that context flag, which would move the state to ``sent``.
            order._send_order_notification_mail(template)
            # Flag the order so the website cart resolver does not resurrect it
            # as an abandoned cart on the customer's next visit. See
            # ``website._get_and_cache_current_cart`` override in this module.
            order.is_skip_payment_quotation = True
        except Exception:
            _logger.exception(
                "Failed to send quotation confirmation email for order %s", order.name
            )
            return request.render(
                "website_sale_checkout_skip_payment.confirmation_order_error"
            )
        request.website.sale_reset()
        values = self._prepare_shop_payment_confirmation_values(order)
        return request.render("website_sale.confirmation", values)
