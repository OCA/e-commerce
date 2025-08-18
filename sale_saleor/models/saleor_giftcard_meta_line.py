# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleorGiftCardMetaLine(models.Model):
    _name = "saleor.giftcard.meta.line"
    _description = "Saleor GiftCard Metadata Line"
    _order = "id"

    giftcard_id = fields.Many2one(
        "saleor.giftcard",
        required=True,
        ondelete="cascade",
    )
    key = fields.Char(required=True)
    value = fields.Char(required=True)


class SaleorGiftCardPrivateMetaLine(models.Model):
    _name = "saleor.giftcard.private.meta.line"
    _description = "Saleor GiftCard Private Metadata Line"
    _order = "id"

    giftcard_id = fields.Many2one(
        "saleor.giftcard",
        required=True,
        ondelete="cascade",
    )
    key = fields.Char(required=True)
    value = fields.Char(required=True)
