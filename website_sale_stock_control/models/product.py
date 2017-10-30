# -*- coding: utf-8 -*-
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import api, fields, models
from openerp.http import request


class WebsiteStockAvailable(models.AbstractModel):
    _name = 'website.stock.available.mixin'

    # To be inherited by other modules
    website_qty_available = fields.Float(
        compute='_compute_website_qty_available')

    @api.multi
    def _compute_website_qty_available(self):
        for product in self:
            product.website_qty_available = product.sudo().with_context(
                force_company=request.env.user.company_id.id
            ).qty_available


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'website.stock.available.mixin']

    # Called the same way as v11 website_sale_stock module
    inventory_availability = fields.Selection([
        ('never', 'Always allow to buy products'),
        ('always', "Don't allow to buy product without stock"),
    ], string='Website Stock Control', default='never',
    )


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = ['product.product', 'website.stock.available.mixin']
