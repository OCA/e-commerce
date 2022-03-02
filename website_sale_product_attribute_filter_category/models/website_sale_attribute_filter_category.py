# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductAttributeCategory(models.Model):
    _inherit = "product.attribute.category"

    website_folded = fields.Boolean(
        string="Website folded",
        default=True,
    )
