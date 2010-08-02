# -*- encoding: utf-8 -*-
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
#from datetime import datetime
import time


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
        'shop_group_ids': fields.one2many('external.shop.group', 'referential_id', 'Sub Entities'),
    }

external_referential()


class product_category(osv.osv):
    _inherit = "product.category"
    
    def collect_children(self, category, children=None):
        if children is None:
            children = []

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
        for shop in self.browse(cr, uid, ids, context=context):
            root_categories = [category for category in shop.exportable_root_category_ids]
            all_categories = []
            for category in root_categories:
                all_categories += [category.id for category in category.recursive_childen_ids]

            # If product_m2mcategories module is installed search in main category and extra categories. If not, only in main category
            cr.execute('select * from ir_module_module where name=%s and state=%s', ('product_m2mcategories','installed'))
            if cr.fetchone():
                product_ids = self.pool.get("product.product").search(cr, uid, ['|',('categ_id', 'in', all_categories),('categ_ids', 'in', all_categories)])
            else:
                product_ids = self.pool.get("product.product").search(cr, uid, [('categ_id', 'in', all_categories)])
            res[shop.id] = product_ids
        return res

    _columns = {
        #'exportable_category_ids': fields.function(_get_exportable_category_ids, method=True, type='one2many', relation="product.category", string='Exportable Categories'),
        'exportable_root_category_ids': fields.many2many('product.category', 'shop_category_rel', 'categ_id', 'shop_id', 'Exportable Root Categories'),
        'exportable_product_ids': fields.function(_get_exportable_product_ids, method=True, type='one2many', relation="product.product", string='Exportable Products'),
        'shop_group_id': fields.many2one('external.shop.group', 'Shop Group', ondelete='cascade'),
        'last_inventory_export_date': fields.datetime('Last Inventory Export Time'),
        'last_images_export_date': fields.datetime('Last Images Export Time'),
        'last_update_order_export_date' : fields.datetime('Last Order Update  Time'),
        'last_products_export_date' : fields.datetime('Last Product Export  Time'),
        'referential_id': fields.related('shop_group_id', 'referential_id', type='many2one', relation='external.referential', string='External Referential'),
        'is_tax_included': fields.boolean('Prices Include Tax?', help="Requires sale_tax_include module to be installed"),
        
        #TODO all the following settings are deprecated and replaced by the finer grained base.sale.payment.type settings!
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
        'payment_default_id': lambda * a: 1, #required field that would cause trouble if not set when importing
        'picking_policy': lambda * a: 'direct',
        'order_policy': lambda * a: 'manual',
        'invoice_quantity': lambda * a: 'order',
        'invoice_generation_policy': lambda * a: 'draft',
        'picking_generation_policy': lambda * a: 'draft',
    }

    def _get_pricelist(self, cr, uid, shop):
        if shop.pricelist_id:
            return shop.pricelist_id.id
        else:
            return self.pool.get('product.pricelist').search(cr, uid, [('type', '=', 'sale'), ('active', '=', True)])[0]
    
    def export_categories(self, cr, uid, shop, ctx=None):
        if ctx is None:
            ctx = {}
        categories = Set([])
        categ_ids = []
        for category in shop.exportable_root_category_ids:
            categ_ids = self.pool.get('product.category')._get_recursive_children_ids(cr, uid, [category.id], "", [], ctx)[category.id]
            for categ_id in categ_ids:
                categories.add(categ_id)
        ctx['shop_id'] = shop.id
        self.pool.get('product.category').ext_export(cr, uid, [categ_id for categ_id in categories], [shop.referential_id.id], {}, ctx)
       
    def export_products_collection(self, cr, uid, shop, products, ctx):
        self.pool.get('product.product').ext_export(cr, uid, [product.id for product in shop.exportable_product_ids] , [shop.referential_id.id], {}, ctx)

    def export_products(self, cr, uid, shop, ctx):
        self.export_products_collection(cr, uid, shop, shop.exportable_product_ids, ctx)
    
    def export_catalog(self, cr, uid, ids, ctx=None):
        if ctx is None:
            ctx = {}
        for shop in self.browse(cr, uid, ids):
            ctx['shop_id'] = shop.id
            ctx['conn_obj'] = self.external_connection(cr, uid, shop.referential_id)
            self.export_categories(cr, uid, shop, ctx)
            self.export_products(cr, uid, shop, ctx)
        self.export_inventory(cr, uid, ids, ctx)
        return False
            
    def export_inventory(self, cr, uid, ids, ctx=None):
        if ctx is None:
            ctx = {}
        for shop in self.browse(cr, uid, ids):
            ctx['shop_id'] = shop.id
            ctx['conn_obj'] = self.external_connection(cr, uid, shop.referential_id)
            product_ids = [product.id for product in shop.exportable_product_ids]
            if shop.last_inventory_export_date:
                recent_move_ids = self.pool.get('stock.move').search(cr, uid, [('date_planned', '>', shop.last_inventory_export_date), ('product_id', 'in', product_ids), ('state', '!=', 'draft'), ('state', '!=', 'cancel')])
            else:
                recent_move_ids = self.pool.get('stock.move').search(cr, uid, [('product_id', 'in', product_ids)])
            product_ids = [move.product_id.id for move in self.pool.get('stock.move').browse(cr, uid, recent_move_ids) if move.product_id.state != 'obsolete']
            product_ids = [x for x in set(product_ids)]
            res = self.pool.get('product.product').export_inventory(cr, uid, product_ids, '', ctx)
            self.pool.get('sale.shop').write(cr, uid, shop.id, {'last_inventory_export_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return res
    
    def import_catalog(self, cr, uid, ids, ctx):
        #TODO import categories, then products
        raise osv.except_osv(_("Not Implemented"), _("Not Implemented in abstract base module!"))
        
    def import_orders(self, cr, uid, ids, ctx=None):
        if ctx is None:
            ctx = {}
        for shop in self.browse(cr, uid, ids):
            ctx['conn_obj'] = self.external_connection(cr, uid, shop.referential_id)
            defaults = {
                            'pricelist_id':self._get_pricelist(cr, uid, shop),
                            'shop_id': shop.id,
                            'picking_policy': shop.picking_policy,
                            'order_policy': shop.order_policy,
                            'invoice_quantity': shop.invoice_quantity
                        }
            if self.pool.get('ir.model.fields').search(cr, uid, [('name', '=', 'company_id'), ('model', '=', 'sale.shop')]): #OpenERP v6 needs a company_id field on the sale order but v5 doesn't have it, same for shop...
                if not shop.company_id.id:
                    raise osv.except_osv(_('Warning!'), _('You have to set a company for this OpenERP sale shop!'))
                defaults.update({'company_id': shop.company_id.id})

            if shop.is_tax_included:
                defaults.update({'price_type': 'tax_included'})

            self.import_shop_orders(cr, uid, shop, defaults, ctx)
        return False
            
    def import_shop_orders(self, cr, uid, shop, defaults, ctx):
        raise osv.except_osv(_("Not Implemented"), _("Not Implemented in abstract base module!"))

    def update_orders(self, cr, uid, ids, ctx=None):
        if ctx is None:
            ctx = {}
        logger = netsvc.Logger()
        for shop in self.browse(cr, uid, ids):
            ctx['conn_obj'] = self.external_connection(cr, uid, shop.referential_id)
            #get all orders, which the state is not draft and the date of modification is superior to the last update, to exports 
            req = "select ir_model_data.res_id, ir_model_data.name from sale_order inner join ir_model_data on sale_order.id = ir_model_data.res_id where ir_model_data.model='sale.order' and sale_order.shop_id=%s and ir_model_data.external_referential_id NOTNULL and sale_order.state != 'draft'"
            param = (shop.id,)

            if shop.last_update_order_export_date:
                req += "and sale_order.write_date > %s" 
                param = (shop.id, shop.last_update_order_export_date)

            cr.execute(req, param)
            results = cr.fetchall()

            for result in results:
                ids = self.pool.get('sale.order').search(cr, uid, [('id', '=', result[0])])
                if ids:
                    id = ids[0]
                    order = self.pool.get('sale.order').browse(cr, uid, id, ctx)            
                    order_ext_id = result[1].split('sale.order_')[1]
                    self.update_shop_orders(cr, uid, order, order_ext_id, ctx)
                    logger.notifyChannel('ext synchro', netsvc.LOG_INFO, "Successfully updated order with OpenERP id %s and ext id %s in external sale system" % (id, order_ext_id))
            self.pool.get('sale.shop').write(cr, uid, shop.id, {'last_update_order_export_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return False

        
    def update_shop_orders(self, cr, uid, order, ext_id, ctx):
        raise osv.except_osv(_("Not Implemented"), _("Not Implemented in abstract base module!"))

    def export_shipping(self, cr, uid, ids, ctx):
        logger = netsvc.Logger()
        for shop in self.browse(cr, uid, ids):
            ctx['conn_obj'] = self.external_connection(cr, uid, shop.referential_id)        
        
            cr.execute("""
                select stock_picking.id, sale_order.id, count(pickings.id) from stock_picking
                left join sale_order on sale_order.id = stock_picking.sale_id
                left join stock_picking as pickings on sale_order.id = pickings.sale_id
                left join ir_model_data on stock_picking.id = ir_model_data.res_id and ir_model_data.model='stock.picking'
                where shop_id = %s and ir_model_data.res_id ISNULL and stock_picking.state = 'done'
                Group By stock_picking.id, sale_order.id
                """, (shop.id,))
            results = cr.fetchall()
            for result in results:
                if result[2] == 1:
                    picking_type = 'complete'
                else:
                    picking_type = 'partial'
                
                ext_shipping_id = self.pool.get('stock.picking').create_ext_shipping(cr, uid, result[0], picking_type, shop.referential_id.id, ctx)

                if ext_shipping_id:
                    ir_model_data_vals = {
                        'name': "stock_picking_" + str(ext_shipping_id),
                        'model': "stock.picking",
                        'res_id': result[0],
                        'external_referential_id': shop.referential_id.id,
                        'module': 'extref.' + shop.referential_id.name
                      }
                    self.pool.get('ir.model.data').create(cr, uid, ir_model_data_vals)
                    logger.notifyChannel('ext synchro', netsvc.LOG_INFO, "Successfully creating shipping with OpenERP id %s and ext id %s in external sale system" % (result[0], ext_shipping_id))

sale_shop()


class sale_order(osv.osv):
    _inherit = "sale.order"

    _columns = {
                'ext_payment_method': fields.char('External Payment Method', size=32, help = "Spree, Magento, Oscommerce... Payment Method"),
                'need_to_update': fields.boolean('Need To Update')
    }
    _defaults = {
        'need_to_update': lambda *a: False,
    }

    def payment_code_to_payment_settings(self, cr, uid, payment_code, ctx=None):
        payment_setting_ids = self.pool.get('base.sale.payment.type').search(cr, uid, [['name', 'ilike', payment_code]])
        return payment_setting_ids and self.pool.get('base.sale.payment.type').browse(cr, uid, payment_setting_ids[0], ctx) or False

    def generate_payment_with_pay_code(self, cr, uid, payment_code, partner_id, amount, payment_ref, entry_name, date, paid, ctx):
        payment_settings = self.payment_code_to_payment_settings(cr, uid, payment_code, ctx)
        if payment_settings and payment_settings.journal_id and (payment_settings.check_if_paid and paid or not payment_settings.check_if_paid):
            return self.generate_payment_with_journal(cr, uid, payment_settings.journal_id.id, partner_id, amount, payment_ref, entry_name, date, payment_settings.validate_payment, ctx)
        return False
        
    def generate_payment_with_journal(self, cr, uid, journal_id, partner_id, amount, payment_ref, entry_name, date, should_validate, ctx):
        statement_vals = {
                            'name': 'ST_' + entry_name,
                            'journal_id': journal_id,
                            'balance_start': 0,
                            'balance_end_real': amount,
                            'date' : date
                        }
        statement_id = self.pool.get('account.bank.statement').create(cr, uid, statement_vals, ctx)
        statement = self.pool.get('account.bank.statement').browse(cr, uid, statement_id, ctx)
        account_id = self.pool.get('account.bank.statement.line').onchange_partner_id(cr, uid, [], partner_id, "customer", statement.currency.id, ctx)['value']['account_id']
        statement_line_vals = {
                                'statement_id': statement_id,
                                'name': entry_name,
                                'ref': payment_ref,
                                'amount': amount,
                                'partner_id': partner_id,
                                'account_id': account_id
                               }
        statement_line_id = self.pool.get('account.bank.statement.line').create(cr, uid, statement_line_vals, ctx)
        if should_validate:
            self.pool.get('account.bank.statement').button_confirm(cr, uid, [statement_id], ctx)
            self.pool.get('account.move.line').write(cr, uid, [statement.move_line_ids[0].id], {'date': date})
        return statement_line_id


    def oe_status(self, cr, uid, order_id, paid = True, context = None):
        wf_service = netsvc.LocalService("workflow")
        order = self.browse(cr, uid, order_id, context)
        payment_settings = self.payment_code_to_payment_settings(cr, uid, order.ext_payment_method, context)
                
        if payment_settings: 
            if payment_settings.check_if_paid and not paid:
                #TODO add update function indeed if automatique import is used sometime you will import an order which is not in a stable state (ex : the order is not payed (waiting for paypal confirmation), and can be payed or canceled later by your e-commerce website)
                self.write(cr, uid, order.id, {'need_to_update': True})
            else:
                if payment_settings.validate_order:
                    wf_service.trg_validate(uid, 'sale.order', order.id, 'order_confirm', cr)
                    
                    if order.order_policy == 'prepaid':
                        if payment_settings.validate_invoice:
                            for invoice in order.invoice_ids:
                                wf_service.trg_validate(uid, 'account.invoice', invoice.id, 'invoice_open', cr)
        
                    if order.order_policy == 'manual':
                        if payment_settings.create_invoice:
                           invoice_id = self.pool.get('sale.order').action_invoice_create(cr, uid, [order_id])
                           if payment_settings.validate_invoice:
                               wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
        
                    # IF postpaid DO NOTHING
        
                    if order.order_policy == 'picking':
                        if payment_settings.create_invoice:
                           invoice_id = self.pool.get('stock.picking').action_invoice_create(cr, uid, order.picking_ids)
                           if payment_settings.validate_invoice:
                               wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)

        return True

    def action_invoice_create(self, cr, uid, ids, grouped=False, states=['confirmed', 'done', 'exception']):
        wf_service = netsvc.LocalService("workflow")
        res = super(sale_order, self).action_invoice_create(cr, uid, ids, grouped, states)
        for order_id in ids:
            order = self.browse(cr, uid, order_id)
            if order.order_policy == 'postpaid':
                payment_settings = self.payment_code_to_payment_settings(cr, uid, order.ext_payment_method)
                if payment_settings and payment_settings.validate_invoice:
                    for invoice in order.invoice_ids:
                        wf_service.trg_validate(uid, 'account.invoice', invoice.id, 'invoice_open', cr)
        return res



sale_order()

class base_sale_payment_type(osv.osv):
    _name = "base.sale.payment.type"
    _description = "Base Sale Payment Type"

    _columns = {
        'name': fields.char('Payment Codes', help="List of Payment Codes separated by ;", size=256, required=True),
        'journal_id': fields.many2one('account.journal','Payment Journal'),
        'picking_policy': fields.selection([('direct', 'Partial Delivery'), ('one', 'Complete Delivery')], 'Packing Policy'),
        'order_policy': fields.selection([
            ('prepaid', 'Payment Before Delivery'),
            ('manual', 'Shipping & Manual Invoice'),
            ('postpaid', 'Invoice on Order After Delivery'),
            ('picking', 'Invoice from the Packing'),
        ], 'Shipping Policy'),
        'invoice_quantity': fields.selection([('order', 'Ordered Quantities'), ('procurement', 'Shipped Quantities')], 'Invoice on'),
        'is_auto_reconcile': fields.boolean('Auto-reconcile?', help="if true will try to reconcile the order payment statement and the open invoice"),
        'validate_order': fields.boolean('Validate Order?'),
        'validate_payment': fields.boolean('Validate Payment?'),
        'create_invoice': fields.boolean('Create Invoice?'),
        'validate_invoice': fields.boolean('Validate Invoice?'),
        'check_if_paid': fields.boolean('Check if Paid?'),
    }
    
    _defaults = {
        'picking_policy': lambda *a: 'direct',
        'order_policy': lambda *a: 'manual',
        'invoice_quantity': lambda *a: 'order',
        'is_auto_reconcile': lambda *a: False,
        'validate_payment': lambda *a: False,
        'validate_invoice': lambda *a: False,
    }

base_sale_payment_type()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
