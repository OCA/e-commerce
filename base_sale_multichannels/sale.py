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
import netsvc
from tools.translate import _


class external_shop_group(external_osv.external_osv):
    _name = 'external.shop.group'
    _description = 'External Referential Shop Group'
    
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'referential_id': fields.many2one('external.referential', 'Referential', select=True, ondelete='cascade'),
        'shop_ids': fields.one2many('sale.shop', 'shop_group_id', 'Sale Shops'),
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
        'referential_id': fields.related('shop_group_id', 'referential_id', type='many2one', relation='external.referential', string='External Referential'),
        'is_tax_included': fields.boolean('Prices Include Tax?', help="Requires sale_tax_include module to be installed"),
        'picking_policy': fields.selection([('direct', 'Partial Delivery'), ('one', 'Complete Delivery')],
                                           'Packing Policy', help="""If you don't have enough stock available to deliver all at once, do you accept partial shipments or not?"""),
        'order_policy': fields.selection([
            ('prepaid', 'Payment Before Delivery'),
            ('manual', 'Shipping & Manual Invoice'),
            ('postpaid', 'Invoice on Order After Delivery'),
            ('picking', 'Invoice from the Packing'),
        ], 'Shipping Policy', help="""The Shipping Policy is used to synchronise invoice and delivery operations.
  - The 'Pay before delivery' choice will first generate the invoice and then generate the packing order after the payment of this invoice.
  - The 'Shipping & Manual Invoice' will create the packing order directly and wait for the user to manually click on the 'Invoice' button to generate the draft invoice.
  - The 'Invoice on Order After Delivery' choice will generate the draft invoice based on sale order after all packing lists have been finished.
  - The 'Invoice from the packing' choice is used to create an invoice during the packing process."""),
        'invoice_quantity': fields.selection([('order', 'Ordered Quantities'), ('procurement', 'Shipped Quantities')], 'Invoice on', help="The sale order will automatically create the invoice proposition (draft invoice). Ordered and delivered quantities may not be the same. You have to choose if you invoice based on ordered or shipped quantities. If the product is a service, shipped quantities means hours spent on the associated tasks."),
        'invoice_generation_policy': fields.selection([('none', 'None'), ('draft', 'Draft'), ('valid', 'Validated')], 'Invoice Generation Policy', help="Should orders create an invoice after import?"),
        'picking_generation_policy': fields.selection([('none', 'None'), ('draft', 'Draft'), ('valid', 'Validated')], 'Picking Generation Policy', help="Should orders create a picking after import?"),
    }
    
    _defaults = {
        'payment_default_id': lambda *a: 1, #required field that would cause trouble if not set when importing
        'picking_policy': lambda *a: 'direct',
        'order_policy': lambda *a: 'manual',
        'invoice_quantity': lambda *a: 'order',
        'invoice_generation_policy': lambda *a: 'draft',
        'picking_generation_policy': lambda *a: 'draft',
    }

    def _get_pricelist(self, cr, uid, shop):
        if shop.pricelist_id:
            return shop.pricelist_id.id
        else:
            return self.pool.get('product.pricelist').search(cr, uid, [('type', '=', 'sale'), ('active', '=', True)])[0]
    
    def export_categories(self, cr, uid, shop, ctx):
        categories = Set([])
        for category in shop.exportable_root_category_ids:
            categ_ids = self.pool.get('product.category')._get_recursive_children_ids(cr, uid, [category.id], "", [], ctx)[category.id]
            for categ_id in categ_ids:
                categories.add(categ_id)
        ctx['shop_id'] = shop.id
        self.pool.get('product.category').ext_export(cr, uid, [categ_id for categ_id in categ_ids], [shop.referential_id.id], {}, ctx)
       
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
            defaults = {
                            'pricelist_id':self._get_pricelist(cr, uid, shop),
                            'shop_id': shop.id,
                            'picking_policy': shop.picking_policy,
                            'order_policy': shop.order_policy,
                            'invoice_quantity': shop.invoice_quantity
                        }
            
            #get last imported order:
            cr.execute("select ir_model_data.name from sale_order inner join ir_model_data on sale_order.id = ir_model_data.res_id where ir_model_data.model='sale.order' and sale_order.shop_id=%s and ir_model_data.external_referential_id NOTNULL order by sale_order.create_date DESC;" % shop.id)
            results = cr.fetchone()
            last_external_id = 0
            if results and len(results) > 0:
                last_external_id = results[0].split('sale.order_')[1]
            ctx['last_external_id'] = last_external_id
            
            if shop.is_tax_included:
                defaults.update({'price_type': 'tax_included'})

            self.import_shop_orders(cr, uid, shop, defaults, ctx)
            
    def import_shop_orders(self, cr, uid, shop, defaults, ctx):
        osv.except_osv(_("Not Implemented"), _("Not Implemented in abstract base module!"))

    def update_orders(self, cr, uid, ids, ctx):
        logger = netsvc.Logger()
        for shop in self.browse(cr, uid, ids):
            ctx['conn_obj'] = self.external_connection(cr, uid, shop.referential_id)
            #get all orders to exports
            cr.execute("select ir_model_data.res_id, ir_model_data.name from sale_order inner join ir_model_data on sale_order.id = ir_model_data.res_id where ir_model_data.model='sale.order' and sale_order.shop_id=%s and ir_model_data.external_referential_id NOTNULL;" % shop.id)
            results = cr.fetchall()
            for result in results:
                ids = self.pool.get('sale.order').search(cr, uid, [('id', '=', result[0])])
                if ids:
                    id = ids[0]
                    order = self.pool.get('sale.order').browse(cr, uid, id, ctx)
                    order_ext_id = result[1].split('sale.order_')[1]
                    self.update_shop_orders(cr, uid, order, order_ext_id, ctx)
                    logger.notifyChannel('ext synchro', netsvc.LOG_INFO, "Successfully updated order with OpenERP id %s and ext id %s in external sale system" %(id, order_ext_id))

        
    def update_shop_orders(self, cr, uid, order, ext_id, ctx):
        osv.except_osv(_("Not Implemented"), _("Not Implemented in abstract base module!"))

sale_shop()