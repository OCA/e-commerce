# -*- coding: utf-8 -*-
# © 2011 Guewen Baconnier,Camptocamp,Elico-Corp
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductLink(models.Model):
    _name = 'product.link'
    _rec_name = 'linked_product_id'

    @api.model
    def get_link_type_selection(self):
        # selection can be inherited and extended
        return [('cross_sell', 'Cross-Sell'),
                ('up_sell', 'Up-Sell'),
                ('related', 'Related')]

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Source Product',
        required=True,
        ondelete='cascade')
    linked_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Linked product',
        required=True,
        ondelete='cascade')
    type = fields.Selection(
        selection='get_link_type_selection',
        string='Link type',
        required=True)
    is_active = fields.Boolean('Active', default=True)


class Product(models.Model):
    _inherit = 'product.product'

    product_link_ids = fields.One2many(
        comodel_name='product.link',
        inverse_name='product_id',
        string='Product links'
    )
