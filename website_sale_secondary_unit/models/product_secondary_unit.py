# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ProductSecondaryUnit(models.Model):
    _inherit = ['product.secondary.unit', 'website.published.mixin']
    _name = 'product.secondary.unit'

    is_published = fields.Boolean(default=True)
