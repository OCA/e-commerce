# Copyright 2025 Tecnativa - Pilar Vargas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    @http.route()
    def payment_confirmation(self, **post):
        res = super().payment_confirmation(**post)
        last_tx = (
            request.env["payment.transaction"]
            .browse(request.session.get("__website_sale_last_tx_id"))
            .sudo()
            .exists()
        )
        if not last_tx or not last_tx.acquirer_id.confirm_order:
            return res
        order = (
            request.env["sale.order"]
            .sudo()
            .browse(request.session.get("sale_last_order_id"))
        )
        if order:
            order.action_confirm()
        request.website.sale_reset()
        return res
