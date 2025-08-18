# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleorVoucherDiscountLine(models.Model):
    _name = "saleor.voucher.discount.line"
    _description = "Saleor Voucher Discount Line"

    voucher_id = fields.Many2one("saleor.voucher", required=True, ondelete="cascade")
    channel_id = fields.Many2one(
        "saleor.channel",
        required=True,
    )
    discount_value = fields.Float()
    currency_id = fields.Many2one(
        "res.currency", related="channel_id.currency_id", readonly=True
    )
    display_unit = fields.Char(
        compute="_compute_display_unit", string="Unit", readonly=True
    )

    _sql_constraints = [
        (
            "unique_voucher_channel",
            "unique(voucher_id, channel_id)",
            "Channel already exists for this voucher.",
        )
    ]

    @api.depends("voucher_id.type", "currency_id")
    def _compute_display_unit(self):
        for line in self:
            if line.voucher_id.type == "fixed":
                line.display_unit = line.currency_id.name or ""
            elif line.voucher_id.type == "percent":
                line.display_unit = "%"
            else:
                line.display_unit = ""
