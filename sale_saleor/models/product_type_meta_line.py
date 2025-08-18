# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTypeMetaLine(models.Model):
    _name = "product.type.meta.line"
    _description = "Product Type Meta Line"

    product_type_id = fields.Many2one(
        "saleor.product.type",
        string="Product Type",
        required=True,
    )
    key = fields.Char(
        required=True,
    )
    value = fields.Char(
        required=True,
    )


class ProductTypePrivateMetaLine(models.Model):
    _name = "product.type.private.meta.line"
    _description = "Product Type Private Meta Line"

    product_type_id = fields.Many2one(
        "saleor.product.type",
        string="Product Type",
        required=True,
    )
    key = fields.Char(
        required=True,
    )
    value = fields.Char(
        required=True,
    )
