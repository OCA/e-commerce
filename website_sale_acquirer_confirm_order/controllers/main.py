# Copyright 2025 Tecnativa - Pilar Vargas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    @http.route()
    def shop_payment_confirmation(self, **post):
        res = super().shop_payment_confirmation(**post)
        sale_order_id = request.session.get("sale_last_order_id")
        if sale_order_id:
            order = request.env["sale.order"].sudo().browse(sale_order_id)
            last_tx = (
                order.get_portal_last_transaction()
                if order
                else order.env["payment.transaction"]
            )
            if (
                not last_tx
                or not last_tx.provider_id.confirm_order
                or order.state == "sale"
            ):
                return res
            order.action_confirm()
            request.website.sale_reset()
        return res
