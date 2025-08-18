# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleorCollectionMetaLine(models.Model):
    _name = "saleor.collection.meta.line"
    _description = "Saleor Collection Metadata Line"
    _order = "id"

    collection_id = fields.Many2one(
        "product.collection", required=True, ondelete="cascade"
    )
    key = fields.Char(required=True)
    value = fields.Char(required=True)


class SaleorCollectionPrivateMetaLine(models.Model):
    _name = "saleor.collection.private.meta.line"
    _description = "Saleor Collection Private Metadata Line"
    _order = "id"

    collection_id = fields.Many2one(
        "product.collection", required=True, ondelete="cascade"
    )
    key = fields.Char(required=True)
    value = fields.Char(required=True)
