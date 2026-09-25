# Copyright 2026 Domatix
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.http import request


class WebsiteSaleDeliveryNote(http.Controller):
    @http.route(
        "/shop/delivery_note",
        type="jsonrpc",
        auth="public",
        website=True,
        methods=["POST"],
    )
    def save_delivery_note(self, delivery_note="", **kwargs):
        """Store the delivery note typed at the checkout on the current cart."""
        order = request.cart
        if order:
            order.sudo().write({"delivery_note": delivery_note})
        return {}
