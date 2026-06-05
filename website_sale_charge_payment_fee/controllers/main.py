# Copyright 2018 Lorenzo Battistini - Agile Business Group
# Copyright 2020 AITIC S.A.S
# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.payment import utils as payment_utils
from odoo.addons.website_sale.controllers.cart import Cart
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.payment import PaymentPortal


def _update_order_fee_from_provider_id(order, provider_id):
    if order and provider_id:
        provider = request.env["payment.provider"].browse(int(provider_id)).exists()
        if provider:
            order.sudo().update_fee_line(provider.sudo())


def _update_payment_context_amount(qcontext, order):
    qcontext["amount"] = order.amount_total
    qcontext["access_token"] = payment_utils.generate_access_token(
        order.partner_invoice_id.id,
        order.amount_total,
        order.currency_id.id,
        env=order.env,
    )


class WebsiteSaleFee(WebsiteSale):
    @http.route(
        "/shop/payment", type="http", auth="public", website=True, sitemap=False
    )
    def shop_payment(self, **post):
        res = super().shop_payment(**post)
        order = request.cart
        provider_id = post.get("provider_id")
        payment_option_id = post.get("payment_option_id")
        payment_methods_sudo = res.qcontext.get("payment_methods_sudo")
        providers_sudo = res.qcontext.get("providers_sudo")
        if payment_option_id:
            res.qcontext["selected_payment_method"] = int(payment_option_id)
        elif payment_methods_sudo and len(payment_methods_sudo) == 1:
            payment_option_id = payment_methods_sudo.id
            res.qcontext["selected_payment_method"] = payment_option_id
        if order and (provider_id or providers_sudo):
            selected_provider = request.env["payment.provider"]
            if provider_id:
                selected_provider = request.env["payment.provider"].browse(
                    int(provider_id)
                )
            elif payment_option_id and payment_methods_sudo:
                selected_method = payment_methods_sudo.filtered(
                    lambda method: method.id == int(payment_option_id)
                )[:1]
                selected_provider = selected_method.provider_ids.filtered(
                    lambda provider: provider in providers_sudo
                )[:1]
            if selected_provider:
                order.sudo().update_fee_line(selected_provider.sudo())
                _update_payment_context_amount(res.qcontext, order)
                res.qcontext["selected_provider"] = selected_provider
        return res

    @http.route()
    def process_express_checkout(self, *args, **kwargs):
        _update_order_fee_from_provider_id(request.cart, kwargs.get("provider_id"))
        return super().process_express_checkout(*args, **kwargs)


class WebsiteSaleFeeCart(Cart):
    def _get_express_shop_payment_values(self, order, **kwargs):
        values = super()._get_express_shop_payment_values(order, **kwargs)
        provider = values.get("providers_sudo", request.env["payment.provider"])[:1]
        if provider:
            order.sudo().update_fee_line(provider.sudo())
            values.update(
                {
                    "amount": order.amount_total,
                    "minor_amount": payment_utils.to_minor_currency_units(
                        order._get_amount_total_excluding_delivery(), order.currency_id
                    ),
                }
            )
        return values


class WebsiteSaleFeePaymentPortal(PaymentPortal):
    @http.route()
    def shop_payment_transaction(self, order_id, access_token, **kwargs):
        order = request.env["sale.order"].sudo().browse(order_id).exists()
        _update_order_fee_from_provider_id(order, kwargs.get("provider_id"))
        return super().shop_payment_transaction(order_id, access_token, **kwargs)
