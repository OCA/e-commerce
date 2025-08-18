# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleorAttributeMetaLine(models.Model):
    _name = "saleor.attribute.meta.line"
    _description = "Saleor Attribute Metadata Line"
    _order = "id"

    attribute_id = fields.Many2one(
        "product.attribute",
        required=True,
        ondelete="cascade",
    )
    key = fields.Char(required=True)
    value = fields.Char(required=True)


class SaleorAttributePrivateMetaLine(models.Model):
    _name = "saleor.attribute.private.meta.line"
    _description = "Saleor Attribute Private Metadata Line"
    _order = "id"

    attribute_id = fields.Many2one(
        "product.attribute",
        required=True,
        ondelete="cascade",
    )
    key = fields.Char(required=True)
    value = fields.Char(required=True)
