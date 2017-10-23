# -*- coding: utf-8 -*-
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    website_qty_available = fields.Float(
        related='qty_available_global', readonly=True, compute_sudo=True)
    website_virtual_available = fields.Float(
        related='virtual_available_global', readonly=True, compute_sudo=True)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    website_qty_available = fields.Float(
        related='qty_available_global', readonly=True, compute_sudo=True)
    website_virtual_available = fields.Float(
        related='virtual_available_global', readonly=True, compute_sudo=True)
