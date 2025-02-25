# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class ProductBrand(models.Model):
    _name = "product.brand"
    _inherit = ["product.brand", "website.published.mixin"]

    is_published = fields.Boolean(default=True)
