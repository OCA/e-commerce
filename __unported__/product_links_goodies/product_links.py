# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   product_links_goodies for OpenERP                                         #
#   Copyright (C) 2012 Akretion Sébastien BEAU <sebastien.beau@akretion.com>  #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from openerp.osv.orm import Model
from openerp.osv import fields
import netsvc
from datetime import datetime

class product_link(Model):
    _inherit = "product.link"
    
    _columns = {
        'quantity': fields.float('Quantity'),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure', help="Unit of Measure for selling or buying this goodies"),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'supplier_goodies': fields.boolean('Supplier Goodies', help=("If it's a supplier goodies "
                                "the product will be automatically added to the purchase order")),
        'cost_price': fields.float('Cost Price'),
    }

    def _get_uom_id(self, cr, uid, *args):
        cr.execute('select id from product_uom order by id limit 1')
        res = cr.fetchone()
        return res and res[0] or False

    _defaults = {
            'uom_id': _get_uom_id,
    }

    def get_link_type_selection(self, cr, uid, context=None):
        res = super(product_link, self).get_link_type_selection(cr, uid, context=context)
        res.append(('goodies', 'Goodies'))
        return res


    def get_quantity(self, cr, uid, ids, qty, context=None):
        link = self.browse(cr, uid, ids[0], context=context)
        return link.quantity * qty

    def run_active_unactive(self, cr, uid, context=None):
        
        to_unactive_ids = self.search(cr, uid, [
                        ['is_active', '=', True],
                        '|',
                            ['end_date', '<', datetime.today().strftime("%Y-%m-%d")],
                            ['start_date', '>', datetime.today().strftime("%Y-%m-%d")]
                        ], context=context)
        self.write(cr, uid, to_unactive_ids, {'is_active': False}, context=context)
        
        to_active_ids = self.search(cr, uid, [
                        ['is_active', '=', True],
                        '|',
                            ['end_date', '>=', datetime.today().strftime("%Y-%m-%d")],
                            ['start_date', '<=', datetime.today().strftime("%Y-%m-%d")]
                        ], context=context)
        self.write(cr, uid, to_active_ids, {'is_active': True}, context=context)

class product_product(Model):
    _inherit = 'product.product'
    
    def _get_supplier_goodies_ids(self, cr, uid, ids, name, arg, context=None):
        if context is None: context={}
        if context.get('date'):
            date = context['date']
        else:
            date = datetime.today().strftime('%Y-%m-%d')
        res = {}
        link_obj = self.pool.get('product.link')
        for product_id in ids:
            res[product_id] = link_obj.search(cr, uid, [
                                    ['product_id','=', ids[0]], 
                                    ['type','=', 'goodies'],
                                    '|', ['start_date', '<=', date], ['start_date', '=', False],
                                    '|', ['end_date', '>=', date], ['end_date', '=', False],
                                    ['supplier_goodies', '=', True],
                            ], context=context)
        return res

    _columns = {
        'supplier_goodies_ids': fields.function(_get_supplier_goodies_ids, type='many2many', relation="product.link"),
    }
    
    def is_purchase_goodies(self, cr, uid, ids, context=None):
        return self.pool.get('product.link').search(cr, uid, [
                                    ['linked_product_id','=', ids[0]], 
                                    ['type', '=', 'goodies'],
                                    ['supplier_goodies', '=', True],
                            ], context=context) and True or False

