# Copyright 2018 Lorenzo Battistini - Agile Business Group
# Copyright 2020 AITIC S.A.S
# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).


from odoo import http
from odoo.exceptions import MissingError
from odoo.http import request

from odoo.addons.website_sale.controllers.main import PaymentPortal, WebsiteSale


class PaymentPortal(PaymentPortal):
    @http.route(
        "/shop/payment/transaction/<int:order_id>",
        type="json",
        auth="public",
        website=True,
    )
    def shop_payment_transaction(self, order_id, access_token, **kwargs):
        res = super().shop_payment_transaction(order_id, access_token, **kwargs)
        try:
            order_sudo = self._document_check_access(
                "sale.order", order_id, access_token
            )
        except MissingError as error:
            raise error

        if kwargs.get("payment_option_id"):
            selected_provider = request.env["payment.provider"].browse(
                int(kwargs.get("payment_option_id"))
            )
            order_sudo.update_fee_line(selected_provider)
        return res


class WebsiteSaleFee(WebsiteSale):
    @http.route(
        ["/shop/payment/get_fee"],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def get_payment_fee(self, provider_id=None, **kw):
        order = request.website.sale_get_order()
        Monetary = request.env["ir.qweb.field.monetary"]

        if not provider_id or not order:
            return {
                "amount_payment_fee": Monetary.value_to_html(
                    0.0, {"display_currency": order.currency_id}
                )
            }

        provider = request.env["payment.provider"].browse(int(provider_id))
        price = order._calculate_payment_fee_price(provider)
        return {
            "amount_payment_fee": Monetary.value_to_html(
                price, {"display_currency": order.currency_id}
            ),
        }
