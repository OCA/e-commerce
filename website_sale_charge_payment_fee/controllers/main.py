# Copyright 2018 Lorenzo Battistini - Agile Business Group
# Copyright 2020 AITIC S.A.S
# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleFee(WebsiteSale):
    @http.route(
        ["/shop/payment/update_fee"],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def update_payment_fee(self, payment_fee_id=None, **kw):
        order = request.website.sale_get_order()
        Monetary = request.env["ir.qweb.field.monetary"]
        result = {
            "amount_payment_fee": Monetary.value_to_html(
                0.0, {"display_currency": order.currency_id}
            )
        }

        if payment_fee_id:
            selected_provider = request.env["payment.provider"].browse(
                int(payment_fee_id)
            )
            order.sudo().update_fee_line(selected_provider.sudo())
            result["amount_payment_fee"] = Monetary.value_to_html(
                order.amount_payment_fee, {"display_currency": order.currency_id}
            )
        return result
