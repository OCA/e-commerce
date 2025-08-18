# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleorGiftCardTag(models.Model):
    _name = "saleor.giftcard.tag"
    _description = "Saleor Gift Card Tag"

    name = fields.Char(required=True)
