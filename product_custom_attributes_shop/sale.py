# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   product_custom_attributes_shop for OpenERP                                 #
#   Copyright (C) 2012 Akretion Benoît GUILLOT <benoit.guillot@akretion.com>  #
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


class sale_shop(Model):
    
    _inherit = "sale.shop"

    def _get_exportable_product_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for shop in self.browse(cr, uid, ids, context=context):
            res[shop.id] = self.pool.get('product.product').search(cr, uid, [['x_shop%s_attr_active'%shop.id, '=', True], ['active', '=', True]], context=context)
        return res

    _columns = {
        'shop_attribute_ids': fields.one2many('attribute.shop.location', 'shop_id', 'Attributes'),
        'exportable_product_ids': fields.function(_get_exportable_product_ids, method=True, type='one2many', relation="product.product", string='Exportable Products'),
    }



    def _prepare_attribute_shop_fields(self, cr, uid, context=None):
        return {'name': 'char', 'description': 'text', 'active': 'boolean'}

    def generate_shop_attributes(self, cr, uid, ids, context=None):
        attr_loc_obj = self.pool.get('attribute.shop.location')
        attr_obj = self.pool.get('product.attribute')
        model_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'product.product')], context=context)[0]
        for shop in self.browse(cr, uid, ids, context=context):
            fields = self._prepare_attribute_shop_fields(cr, uid, context=context)
            for field, field_type in fields.items():
                attribute_loc_ids = attr_loc_obj.search(cr, uid, [('shop_id', '=', shop.id),('external_name', '=', field)], context=context)
                if not attribute_loc_ids:
                    field_name = 'x_shop%s_attr_%s' %(shop.id, field)
                    prod_attribute_ids = attr_obj.search(cr, uid, [('name', '=', field_name)], context=context)
                    if not prod_attribute_ids:
                        vals = {
                                'name': field_name, 
                                'field_description': field, 
                                'attribute_type': field_type, 
                                'based_on': 'product_product',
                                'translate': field_type in ('char', 'text'),
                                }
                        prod_attribute_id = attr_obj.create(cr, uid, vals, context=context)
                    else:
                        prod_attribute_id = prod_attribute_ids[0]
                    attribute_id = attr_loc_obj.create(cr, uid, {
                                    'external_name': field,
                                    'attribute_id': prod_attribute_id,
                                    'shop_id': shop.id
                                                }, context=context)
                    attribute_loc_ids.append(attribute_id)
        return attribute_loc_ids


