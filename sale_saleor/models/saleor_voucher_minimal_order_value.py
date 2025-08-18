# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleorVoucherMinimalOrderValue(models.Model):
    _name = "saleor.voucher.minimal.order.value"
    _description = "Saleor Voucher Minimal Order Value"

    voucher_id = fields.Many2one("saleor.voucher", required=True, ondelete="cascade")
    channel_id = fields.Many2one(
        "saleor.channel",
        required=True,
    )
    minimal_order_value = fields.Float()

    _sql_constraints = [
        (
            "unique_voucher_channel",
            "unique(voucher_id, channel_id)",
            "Channel already exists for this voucher.",
        ),
        (
            "check_minimal_order_value_nonnegative",
            "CHECK(minimal_order_value >= 0)",
            "Minimal order value must be greater than or equal to 0.",
        ),
    ]
