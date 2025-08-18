# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    saleor_customer_id = fields.Char(
        string="Saleor Customer ID",
        index=True,
        copy=False,
        help="ID of the customer record in Saleor",
    )
    saleor_account_id = fields.Many2one(
        "saleor.account",
        string="Saleor Account",
        copy=False,
        help="Saleor account this customer is linked to",
    )
