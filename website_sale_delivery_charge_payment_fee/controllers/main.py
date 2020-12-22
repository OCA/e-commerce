# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleFee(WebsiteSale):
    @http.route(
        ["/shop/update_payment_fee"],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
        csrf=False,
    )
    def update_payment_fee(self, **post):
        order = request.website.sale_get_order()
        acquirer_id = post.get("acquirer_id")
        if acquirer_id:
            acquirer = request.env["payment.acquirer"].browse(int(acquirer_id))
            order.sudo().update_fee_line(acquirer.sudo())
        if "carrier_id" not in post:
            post["carrier_id"] = order.carrier_id.id
        results = self._update_website_sale_delivery_return(order, **post)
        results["amount_payment_fee"] = order.amount_payment_fee
        return results
