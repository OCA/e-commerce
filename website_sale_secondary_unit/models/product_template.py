# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    allow_uom_sell = fields.Boolean(
        string='Allow to sell in unit of measure',
        default=True,
    )
