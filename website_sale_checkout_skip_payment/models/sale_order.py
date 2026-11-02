# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    website_payment_skipped = fields.Boolean(
        readonly=True,
        index=True,
        help="This is checked if the sale order has been confirmed with a partner "
        "that can skip payment",
    )
