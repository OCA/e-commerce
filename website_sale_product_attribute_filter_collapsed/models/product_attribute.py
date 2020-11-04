# Copyright 2020 Iván Todorovich
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductAttributeCategory(models.Model):
    _inherit = "product.attribute"

    website_folded = fields.Boolean(
        string="Website folded",
        default=True,
    )
