# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ProductAttribute(models.Model):
    _inherit = ['product.attribute', 'website.published.mixin']
    _name = 'product.attribute'
