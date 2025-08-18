# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleorTaxMetaLine(models.Model):
    _name = "saleor.tax.meta.line"
    _description = "Saleor Tax Metadata Line"
    _order = "id"

    tax_id = fields.Many2one(
        "account.tax",
        required=True,
        ondelete="cascade",
    )
    key = fields.Char(required=True)
    value = fields.Char(required=True)


class SaleorTaxPrivateMetaLine(models.Model):
    _name = "saleor.tax.private.meta.line"
    _description = "Saleor Tax Private Metadata Line"
    _order = "id"

    tax_id = fields.Many2one(
        "account.tax",
        required=True,
        ondelete="cascade",
    )
    key = fields.Char(required=True)
    value = fields.Char(required=True)
