# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    confirm_order = fields.Boolean(
        string="Confirm Order Automatically",
        help="If enabled, orders paid with this method will be automatically "
        "confirmed.",
    )
