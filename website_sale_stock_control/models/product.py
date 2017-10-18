# -*- coding: utf-8 -*-
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    inventory_availability = fields.Selection([
        ('never', 'Allow buy products without control'),
        ('always', 'Deny buy products without stock'),
    ], string='Stock Control', default='never',
    )
    # To be inherit by other modules
    website_qty_available = fields.Float(
        related='qty_available', readonly=True)
    website_virtual_available = fields.Float(
        related='virtual_available', readonly=True)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    website_qty_available = fields.Float(
        related='qty_available', readonly=True)
    website_virtual_available = fields.Float(
        related='virtual_available', readonly=True)
