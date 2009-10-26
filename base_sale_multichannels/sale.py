# -*- encoding: utf-8 -*-
#########################################################################
#                                                                       #
#########################################################################
#                                                                       #
# Copyright (C) 2009  Raphaël Valyi                                     #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################

from osv import osv, fields
from base_external_referentials import external_osv
from sets import Set


class external_shop_group(external_osv.external_osv):
    _name = 'external.shop.group'
    _description = 'External Referential Shop Group'
    
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'referential_id': fields.many2one('external.referential', 'Referential', select=True, ondelete='cascade'),
        'shop_ids': fields.one2many('sale.shop', 'entity_id', 'Sale Shops'),
    }
    
external_shop_group()


class external_referential(osv.osv):
    _inherit = 'external.referential'
    
    _columns = {
        'entity_ids': fields.one2many('external.shop.group', 'referential_id', 'Sub Entities'),
    }

external_referential()


class product_category(osv.osv):
    _inherit = "product.category"
    
    def collect_children(self, category, children=[]):
        for child in category.child_id:
            children.append(child.id)
            self.collect_children(child, children)
        return children
    
    def _get_recursive_children_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for category in self.browse(cr, uid, ids):
            res[category.id] = self.collect_children(category, [category.id])
        return res

    _columns = {
        'recursive_childen_ids': fields.function(_get_recursive_children_ids, method=True, type='one2many', relation="product.category", string='All Child Categories'),
    }
    
product_category()


class sale_shop(external_osv.external_osv):
    _inherit = "sale.shop"

    def _get_exportable_product_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for shop in self.browse(cr, uid, ids):
            root_categories = [category for category in shop.exportable_root_category_ids]
            all_categories = []
            for category in root_categories:
                all_categories += [category.id for category in category.recursive_childen_ids]
            product_ids = self.pool.get("product.product").search(cr, uid, [('categ_id','in', all_categories)]) #TODO deal with product_m2mactegories module
            res[shop.id] = product_ids
        return res

    _columns = {
        #'exportable_category_ids': fields.function(_get_exportable_category_ids, method=True, type='one2many', relation="product.category", string='Exportable Categories'),
        'exportable_root_category_ids': fields.many2many('product.category', 'shop_category_rel', 'categ_id', 'shop_id', 'Exportable Root Categories'),
        'exportable_product_ids': fields.function(_get_exportable_product_ids, method=True, type='one2many', relation="product.product", string='Exportable Products'),
        'shop_group_id':fields.many2one('external.shop.group', 'Shop Group', ondelete='cascade'),
        'referential_id': fields.related('shop_group_id', 'referential_id', type='many2one', relation='external.referential', string='External Referential')
    }
    
    _defaults = {
        'payment_default_id': lambda *a: 1, #required field that would cause trouble if not set when importing
    }
    
    def export_categories(self, cr, uid, shop, ctx):
        categories = Set([])
        for category in shop.exportable_root_category_ids:#TODO ensure order is from root to leaf
            for child in category.recursive_childen_ids:
                categories.add(child)
        ctx['shop_id'] = shop.id
        self.pool.get('product.category').ext_export(cr, uid, [categ.id for categ in categories], [shop.referential_id.id], {}, ctx)
       
    def export_products_collection(self, cr, uid, shop, products, ctx):
        self.pool.get('product.product').ext_export(cr, uid, [product.id for product in shop.exportable_product_ids] ,[shop.referential_id.id], {}, ctx)

    def export_products(self, cr, uid, shop, ctx):
        self.export_products_collection(cr, uid, shop, shop.exportable_product_ids, ctx)
    
    def export_catalog(self, cr, uid, ids, ctx):
        for shop in self.browse(cr, uid, ids):
            ctx['shop_id'] = shop.id
            ctx['conn_obj'] = self.external_connection(cr, uid, shop.referential_id)
            self.export_categories(cr, uid, shop, ctx)
            self.export_products(cr, uid, shop, ctx)
        
    def import_catalog(self, cr, uid, ids, ctx):
        #TODO import categories, then products
        osv.except_osv(_("Not Implemented"), _("Not Implemented in abstract base module!"))
        
    def import_orders(self, cr, uid, ids, ctx):
        for shop in self.browse(cr, uid, ids):
            ctx['conn_obj'] = self.external_connection(cr, uid, shop.referential_id)
            self.import_shop_orders(cr, uid, shop, ctx)
            
    def import_shop_orders(self, cr, uid, shop, ctx):
        osv.except_osv(_("Not Implemented"), _("Not Implemented in abstract base module!"))

    def update_orders(self, cr, uid, ids, ctx):
        for shop in self.browse(cr, uid, ids):
            ext_connection = self.external_connection(cr, uid, shop.referential_id)
            if ext_connection:
                self.update_shop_orders(cr, uid, shop, ctx)
        
    def update_shop_orders(self, cr, uid, shop, ctx):
        osv.except_osv(_("Not Implemented"), _("Not Implemented in abstract base module!"))

sale_shop()