# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.http import Controller, request, route


class CreditController(Controller):
    _process_url = "/payment/credit/process"

    @route(_process_url, type="http", auth="public", methods=["POST"], csrf=False)
    def custom_process_transaction(self, **post):
        request.env["payment.transaction"].sudo()._handle_notification_data(
            "credit", post
        )
        return request.redirect("/payment/status")
