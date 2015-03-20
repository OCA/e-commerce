# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields


class ProductLink(models.Model):
    _name = 'product.link'
    _rec_name = 'linked_product_id'

    product_id = fields.Many2one(
        comodel_name='product.template',
        string='Soruce Product',
        required=True,
        ondelete='cascade',
        default=lambda self: self.env.context.get('product_id', False))
    linked_product_id = fields.Many2one(
        comodel_name='product.template',
        string='Linked product',
        required=True,
        ondelete='cascade')
    type = fields.Selection(
        selection=[
            ('cross_sell', 'Cross-Sell'),
            ('up_sell', 'Up-Sell'),
            ('related', 'Related')],
        string='Link type',
        required=True)
    is_active = fields.Boolean('Active', defalut=True)


class Product(models.Model):
    _inherit = 'product.template'

    product_link_ids = fields.One2many(
        comodel_name='product.link',
        inverse_name='product_id',
        string='Product links'
    )
