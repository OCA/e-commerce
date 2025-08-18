# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleorCategoryMetaLine(models.Model):
    _name = "saleor.category.meta.line"
    _description = "Saleor Category Metadata Line"
    _order = "id"

    category_id = fields.Many2one("product.category", required=True, ondelete="cascade")
    key = fields.Char(required=True)
    value = fields.Char(required=True)


class SaleorCategoryPrivateMetaLine(models.Model):
    _name = "saleor.category.private.meta.line"
    _description = "Saleor Category Private Metadata Line"
    _order = "id"

    category_id = fields.Many2one("product.category", required=True, ondelete="cascade")
    key = fields.Char(required=True)
    value = fields.Char(required=True)
