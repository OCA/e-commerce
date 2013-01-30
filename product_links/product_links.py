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

from openerp.osv import orm, fields


class product_link(orm.Model):
    _name = 'product.link'
    _rec_name = 'linked_product_id'

    def get_link_type_selection(self, cr, uid, context=None):
        # selection can be inherited and extended
        return [('cross_sell', 'Cross-Sell'),
                ('up_sell', 'Up-Sell'),
                ('related', 'Related')]

    def _get_link_type_selection(self, cr, uid, context=None):
        return self.get_link_type_selection(cr, uid, context=context)

    _columns = {
        'product_id': fields.many2one(
            'product.product',
            'Source product',
            required=True,
            ondelete='cascade'),
        'linked_product_id': fields.many2one(
            'product.product',
            'Linked product',
            required=True,
            ondelete='cascade'),
        'type': fields.selection(
            _get_link_type_selection,
            string='Link type',
            required=True),
        'is_active': fields.boolean('Active'),
    }

    # It seems that it's not possible to set the default value of a field in
    # a one2many via the context (it works well with a many2one though)
    # So I have to set explicitly a default value
    def _get_default_product_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('product_id', False)

    _defaults = {
        'is_active': True,
        'product_id': _get_default_product_id,
    }


class product(orm.Model):
    _inherit = 'product.product'

    _columns = {
        'product_link_ids': fields.one2many(
            'product.link',
            'product_id',
            string='Product links'),
        }
