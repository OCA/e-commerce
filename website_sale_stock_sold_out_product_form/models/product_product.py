# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_sold_out = fields.Boolean(compute="_compute_is_sold_out")

    def _compute_is_sold_out(self):
        for product in self:
            product.is_sold_out = product._is_sold_out()
