# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleorVoucherMetaLine(models.Model):
    _name = "saleor.voucher.meta.line"
    _description = "Saleor Voucher Metadata Line"
    _order = "id"

    voucher_id = fields.Many2one(
        "saleor.voucher",
        required=True,
        ondelete="cascade",
    )
    key = fields.Char(required=True)
    value = fields.Char(required=True)


class SaleorVoucherPrivateMetaLine(models.Model):
    _name = "saleor.voucher.private.meta.line"
    _description = "Saleor Voucher Private Metadata Line"
    _order = "id"

    voucher_id = fields.Many2one(
        "saleor.voucher",
        required=True,
        ondelete="cascade",
    )
    key = fields.Char(required=True)
    value = fields.Char(required=True)
