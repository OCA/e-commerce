# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleorProductMetaLine(models.Model):
    _name = "saleor.product.meta.line"
    _description = "Saleor Product Metadata Line"
    _order = "id"

    product_tmpl_id = fields.Many2one(
        "product.template", required=True, ondelete="cascade"
    )
    key = fields.Char(required=True)
    value = fields.Char(required=True)


class SaleorProductPrivateMetaLine(models.Model):
    _name = "saleor.product.private.meta.line"
    _description = "Saleor Product Private Metadata Line"
    _order = "id"

    product_tmpl_id = fields.Many2one(
        "product.template", required=True, ondelete="cascade"
    )
    key = fields.Char(required=True)
    value = fields.Char(required=True)
