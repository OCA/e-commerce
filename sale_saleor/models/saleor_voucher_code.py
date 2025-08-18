# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleorVoucherCode(models.Model):
    _name = "saleor.voucher.code"
    _description = "Saleor Voucher Code"

    voucher_id = fields.Many2one(
        "saleor.voucher",
        required=True,
        ondelete="cascade",
    )
    code = fields.Char(required=True)
    usage = fields.Integer()
    status = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("active", "Active"),
            ("inactive", "Inactive"),
        ],
        required=True,
        default="draft",
    )
    _sql_constraints = [
        (
            "saleor_voucher_code_unique",
            "unique(code)",
            "Voucher code already exists. Please use a unique code.",
        )
    ]

    @api.constrains("code")
    def _check_unique_code(self):
        for rec in self:
            if not rec.code:
                continue
            dup = self.search(
                [
                    ("id", "!=", rec.id),
                    ("code", "=", rec.code),
                ],
                limit=1,
            )
            if dup:
                raise ValidationError(
                    self.env._("Voucher code '%s' already exists.", rec.code)
                )
