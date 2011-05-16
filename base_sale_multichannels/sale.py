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
from sets import Set as set
import netsvc
from tools.translate import _
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class external_shop_group(osv.osv):
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

class sale_shop(osv.osv):
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
        'sale_journal': fields.many2one('account.journal', 'Sale Journal'),
    }
    
    _defaults = {
        'payment_default_id': lambda * a: 1, #required field that would cause trouble if not set when importing
    }

    def _get_pricelist(self, cr, uid, shop):
        if shop.pricelist_id:
            return shop.pricelist_id.id
        else:
            return self.pool.get('product.pricelist').search(cr, uid, [('type', '=', 'sale'), ('active', '=', True)])[0]
    
    def export_categories(self, cr, uid, shop, context=None):
        if context is None:
            context = {}
        categories = set([])
        categ_ids = []
        for category in shop.exportable_root_category_ids:
            categ_ids = self.pool.get('product.category')._get_recursive_children_ids(cr, uid, [category.id], "", [], context)[category.id]
            for categ_id in categ_ids:
                categories.add(categ_id)
        context['shop_id'] = shop.id
        self.pool.get('product.category').ext_export(cr, uid, [categ_id for categ_id in categories], [shop.referential_id.id], {}, context)
       
    def export_products_collection(self, cr, uid, shop, context):
        product_to_export = context.get('force_product_ids', [product.id for product in shop.exportable_product_ids])
        self.pool.get('product.product').ext_export(cr, uid, product_to_export, [shop.referential_id.id], {}, context)

    def export_products(self, cr, uid, shop, context):
        self.export_products_collection(cr, uid, shop, context)
    
    def export_catalog(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        report_obj = self.pool.get('external.report')
        for shop in self.browse(cr, uid, ids):
            context['shop_id'] = shop.id
            report_id = report_obj.start_report(cr, uid,
                                                ref='export_catalog',
                                                external_referential_id=shop.referential_id.id,
                                                context=context)
            context['external_report_id'] = report_id
            context['conn_obj'] = self.external_connection(cr, uid, shop.referential_id)
            self.export_categories(cr, uid, shop, context)
            self.export_products(cr, uid, shop, context)
            shop.write({'last_products_export_date' : time.strftime('%Y-%m-%d %H:%M:%S')})
            report_obj.end_report(cr, uid, report_id, context=context)
        self.export_inventory(cr, uid, ids, context)
        return False
            
    def export_inventory(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for shop in self.browse(cr, uid, ids):
            context['shop_id'] = shop.id
            context['conn_obj'] = self.external_connection(cr, uid, shop.referential_id)
            product_ids = [product.id for product in shop.exportable_product_ids]
            if shop.last_inventory_export_date:
                # we do not exclude canceled moves because it means some stock levels could have increased since last export
                recent_move_ids = self.pool.get('stock.move').search(cr, uid, [('write_date', '>', shop.last_inventory_export_date), ('product_id', 'in', product_ids), ('state', '!=', 'draft')])
            else:
                recent_move_ids = self.pool.get('stock.move').search(cr, uid, [('product_id', 'in', product_ids)])
            product_ids = [move.product_id.id for move in self.pool.get('stock.move').browse(cr, uid, recent_move_ids) if move.product_id.state != 'obsolete']
            product_ids = [x for x in set(product_ids)]
            res = self.pool.get('product.product').export_inventory(cr, uid, product_ids, '', context)
            shop.write({'last_inventory_export_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return res
    
    def import_catalog(self, cr, uid, ids, context):
        #TODO import categories, then products
        raise osv.except_osv(_("Not Implemented"), _("Not Implemented in abstract base module!"))
        
    def import_orders(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for shop in self.browse(cr, uid, ids):
            context['conn_obj'] = self.external_connection(cr, uid, shop.referential_id)
            defaults = {
                            'pricelist_id':self._get_pricelist(cr, uid, shop),
                            'shop_id': shop.id,
                        }
            if self.pool.get('ir.model.fields').search(cr, uid, [('name', '=', 'company_id'), ('model', '=', 'sale.shop')]): #OpenERP v6 needs a company_id field on the sale order but v5 doesn't have it, same for shop...
                if not shop.company_id.id:
                    raise osv.except_osv(_('Warning!'), _('You have to set a company for this OpenERP sale shop!'))
                defaults.update({'company_id': shop.company_id.id})

            if shop.is_tax_included:
                defaults.update({'price_type': 'tax_included'})

            defaults.update(self.pool.get('sale.order').onchange_shop_id(cr, uid, ids, shop.id)['value'])

            self.import_shop_orders(cr, uid, shop, defaults, context)
        return False
            
    def import_shop_orders(self, cr, uid, shop, defaults, context):
        raise osv.except_osv(_("Not Implemented"), _("Not Implemented in abstract base module!"))

    def update_orders(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        logger = netsvc.Logger()
        for shop in self.browse(cr, uid, ids):
            context['conn_obj'] = self.external_connection(cr, uid, shop.referential_id)
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
                    order = self.pool.get('sale.order').browse(cr, uid, id, context)
                    order_ext_id = result[1].split('sale_order/')[1]
                    self.update_shop_orders(cr, uid, order, order_ext_id, context)
                    logger.notifyChannel('ext synchro', netsvc.LOG_INFO, "Successfully updated order with OpenERP id %s and ext id %s in external sale system" % (id, order_ext_id))
            self.pool.get('sale.shop').write(cr, uid, shop.id, {'last_update_order_export_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return False

    def update_shop_partners(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context.update({'force': True}) #FIXME
        for shop in self.browse(cr, uid, ids):
            context['conn_obj'] = self.external_connection(cr, uid, shop.referential_id)
            ids = self.pool.get('res.partner').search(cr, uid, [('store_id', '=', self.pool.get('sale.shop').oeid_to_extid(cr, uid, shop.id, shop.referential_id.id, context))])
            self.pool.get('res.partner').ext_export(cr, uid, ids, [shop.referential_id.id], {}, context)
        return True
        
    def update_shop_orders(self, cr, uid, order, ext_id, context):
        raise osv.except_osv(_("Not Implemented"), _("Not Implemented in abstract base module!"))

    def export_shipping(self, cr, uid, ids, context):
        logger = netsvc.Logger()
        for shop in self.browse(cr, uid, ids):
            context['conn_obj'] = self.external_connection(cr, uid, shop.referential_id)        
        
            cr.execute("""
                select stock_picking.id, sale_order.id, count(pickings.id),
                       delivery_carrier.export_needs_tracking, stock_picking.carrier_tracking_ref
                from stock_picking
                left join sale_order on sale_order.id = stock_picking.sale_id
                left join stock_picking as pickings on sale_order.id = pickings.sale_id
                left join ir_model_data on stock_picking.id = ir_model_data.res_id and ir_model_data.model='stock.picking'
                left join delivery_carrier on delivery_carrier.id = stock_picking.carrier_id
                where shop_id = %s and ir_model_data.res_id ISNULL and stock_picking.state = 'done'
                Group By stock_picking.id, sale_order.id,
                         delivery_carrier.export_needs_tracking, stock_picking.carrier_tracking_ref
                """, (shop.id,))
            results = cr.fetchall()
            for result in results:
                if result[2] == 1:
                    picking_type = 'complete'
                else:
                    picking_type = 'partial'

               # only export the shipping if a tracking number exists when the flag
               # export_needs_tracking is flagged on the delivery carrier
                if result[3] and not result[4]:
                    continue
                
                ext_shipping_id = self.pool.get('stock.picking').create_ext_shipping(cr, uid, result[0], picking_type, shop.referential_id.id, context)

                if ext_shipping_id:
                    ir_model_data_vals = {
                        'name': "stock_picking/" + str(ext_shipping_id),
                        'model': "stock.picking",
                        'res_id': result[0],
                        'external_referential_id': shop.referential_id.id,
                        'module': 'extref/' + shop.referential_id.name
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

    def payment_code_to_payment_settings(self, cr, uid, payment_code, context=None):
        pay_type_obj = self.pool.get('base.sale.payment.type')
        payment_setting_ids = pay_type_obj.search(cr, uid, [['name', 'like', payment_code]])
        payment_setting_id = False
        for type in pay_type_obj.read(cr, uid, payment_setting_ids, fields=['name'], context=context):
            if payment_code in [x.strip() for x in type['name'].split(';')]:
                payment_setting_id = type['id']
        return payment_setting_id and pay_type_obj.browse(cr, uid, payment_setting_id, context) or False

    def generate_payment_with_pay_code(self, cr, uid, payment_code, partner_id, amount, payment_ref, entry_name, date, paid, context):
        payment_settings = self.payment_code_to_payment_settings(cr, uid, payment_code, context)
        if payment_settings and payment_settings.journal_id and (payment_settings.check_if_paid and paid or not payment_settings.check_if_paid):
            return self.generate_payment_with_journal(cr, uid, payment_settings.journal_id.id, partner_id, amount, payment_ref, entry_name, date, payment_settings.validate_payment, context)
        return False
        
    def generate_payment_with_journal(self, cr, uid, journal_id, partner_id, amount, payment_ref, entry_name, date, should_validate, context):
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        data = voucher_obj.onchange_partner_id(cr, uid, [], partner_id, journal_id, int(amount), False, 'receipt', date, context)['value']
        account_id = data['account_id']
        currency_id = data['currency_id']
        statement_vals = {
                            'reference': 'ST_' + entry_name,
                            'journal_id': journal_id,
                            'amount': amount,
                            'date' : date,
                            'partner_id': partner_id,
                            'account_id': account_id,
                            'type': 'receipt',
                            'currency_id': currency_id,
                        }
        statement_id = voucher_obj.create(cr, uid, statement_vals, context)
        context.update({'type': 'receipt', 'partner_id': partner_id, 'journal_id': journal_id, 'default_type': 'cr'})
        line_account_id = voucher_line_obj.default_get(cr, uid, ['account_id'], context)['account_id']
        statement_line_vals = {
                                'voucher_id': statement_id,
                                'amount': amount,
                                'account_id': line_account_id,
                                'type': 'cr',
                               }
        statement_line_id = voucher_line_obj.create(cr, uid, statement_line_vals, context)
        if should_validate:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'account.voucher', statement_id, 'proforma_voucher', cr)
        return statement_id


    def oe_status(self, cr, uid, order_id, paid = True, context = None):
        wf_service = netsvc.LocalService("workflow")
        logger = netsvc.Logger()
        order = self.browse(cr, uid, order_id, context)
        payment_settings = self.payment_code_to_payment_settings(cr, uid, order.ext_payment_method, context)
                
        if payment_settings:
            if payment_settings.payment_term_id:
                self.write(cr, uid, order.id, {'payment_term': payment_settings.payment_term_id.id})

            if payment_settings.check_if_paid and not paid:
                if order.state == 'draft' and datetime.strptime(order.date_order, '%Y-%m-%d') < datetime.now() - relativedelta(days=payment_settings.days_before_order_cancel or 30):
                    wf_service.trg_validate(uid, 'sale.order', order.id, 'cancel', cr)
                    self.write(cr, uid, order.id, {'need_to_update': False})
                    self.log(cr, uid, order.id, "order %s canceled in OpenERP because older than % days and still not confirmed" % (order.id, payment_settings.days_before_order_cancel or 30))
                    #TODO eventually call a trigger to cancel the order in the external system too
                    logger.notifyChannel('ext synchro', netsvc.LOG_INFO, "order %s canceled in OpenERP because older than % days and still not confirmed" % (order.id, payment_settings.days_before_order_cancel or 30))
                else:
                    self.write(cr, uid, order.id, {'need_to_update': True})
            else:
                if payment_settings.validate_order:
                    try:
                        wf_service.trg_validate(uid, 'sale.order', order.id, 'order_confirm', cr)
                        self.write(cr, uid, order.id, {'need_to_update': False})
                    except Exception, e:
                        self.log(cr, uid, order.id, "ERROR could not valid order")
                    
                    if payment_settings.validate_picking:
                        self.pool.get('stock.picking').validate_picking(cr, uid, order_id)
                    
                    cr.execute('select * from ir_module_module where name=%s and state=%s', ('mrp','installed'))
                    if payment_settings.validate_manufactoring_order and cr.fetchone(): #if mrp module is installed
                        self.pool.get('stock.picking').validate_manufactoring_order(cr, uid, order_id, context)

                    if order.order_policy == 'prepaid':
                        if payment_settings.validate_invoice:
                            for invoice in order.invoice_ids:
                                wf_service.trg_validate(uid, 'account.invoice', invoice.id, 'invoice_open', cr)
                                if payment_settings.is_auto_reconcile:
                                    invoice.auto_reconcile(context=context)
        
                    elif order.order_policy == 'manual':
                        if payment_settings.create_invoice:
                           wf_service.trg_validate(uid, 'sale.order', order_id, 'manual_invoice', cr)
                           invoice_id = self.browse(cr, uid, order_id).invoice_ids[0].id
                           if payment_settings.validate_invoice:
                               wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                               if payment_settings.is_auto_reconcile:
                                   self.pool.get('account.invoice').auto_reconcile(cr, uid, [invoice_id], context=context)
        
                    # IF postpaid DO NOTHING
        
                    elif order.order_policy == 'picking':
                        if payment_settings.create_invoice:
                            try:
                                invoice_id = self.pool.get('stock.picking').action_invoice_create(cr, uid, [picking.id for picking in order.picking_ids])
                            except Exception, e:
                                self.log(cr, uid, order.id, "Cannot create invoice from picking for order %s" %(order.name,))
                            if payment_settings.validate_invoice:
                                wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                                if payment_settings.is_auto_reconcile:
                                    self.pool.get('account.invoice').auto_reconcile(cr, uid, [invoice_id], context=context)

        return True


    def _make_invoice(self, cr, uid, order, lines, context={}):
        inv_id = super(sale_order, self)._make_invoice(cr, uid, order, lines, context)
        if order.shop_id.sale_journal:
            self.pool.get('account.invoice').write(cr, uid, [inv_id], {'journal_id' : order.shop_id.sale_journal.id}, context=context)
        return inv_id

    def action_invoice_create(self, cr, uid, ids, grouped=False, states=['confirmed', 'done', 'exception'], date_inv = False, context=None):
        inv_obj = self.pool.get('account.invoice')
        wf_service = netsvc.LocalService("workflow")
        res = super(sale_order, self).action_invoice_create(cr, uid, ids, grouped, states, date_inv, context)
        
        for order in self.browse(cr, uid, ids, context=context):
            payment_settings = self.payment_code_to_payment_settings(cr, uid, order.ext_payment_method, context=context)
            if payment_settings and payment_settings.invoice_date_is_order_date:
                inv_obj.write(cr, uid, [inv.id for inv in order.invoice_ids], {'date_invoice' : order.date_order}, context=context)
            if order.order_policy == 'postpaid':
                if payment_settings and payment_settings.validate_invoice:
                    for invoice in order.invoice_ids:
                        wf_service.trg_validate(uid, 'account.invoice', invoice.id, 'invoice_open', cr)
                        if payment_settings.is_auto_reconcile:
                            invoice.auto_reconcile(context=context)
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
        'validate_picking': fields.boolean('Validate Picking?'),
        'validate_manufactoring_order': fields.boolean('Validate Manufactoring Order?'),
        'check_if_paid': fields.boolean('Check if Paid?'),
        'days_before_order_cancel': fields.integer('Days Delay before Cancel', help='number of days before an unpaid order will be cancelled at next status update from Magento'),
        'invoice_date_is_order_date' : fields.boolean('Force Invoice Date?', help="If it's check the invoice date will be the same as the order date"),
        'payment_term_id': fields.many2one('account.payment.term', 'Payment Term'),
    }
    
    _defaults = {
        'picking_policy': lambda *a: 'direct',
        'order_policy': lambda *a: 'manual',
        'invoice_quantity': lambda *a: 'order',
        'is_auto_reconcile': lambda *a: False,
        'validate_payment': lambda *a: False,
        'validate_invoice': lambda *a: False,
        'days_before_order_cancel': lambda *a: 30,
    }

base_sale_payment_type()

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def auto_reconcile(self, cr, uid, ids, context=None):
        obj_move_line = self.pool.get('account.move.line')
        for invoice in self.browse(cr, uid, ids, context=context):
            line_ids = obj_move_line.search(cr, uid, ['|', ['ref', 'ilike', invoice.origin], ['ref', '=', invoice.move_id.ref], ['account_id', '=', invoice.account_id.id]], context=context)
            if len(line_ids) == 2:
                lines = obj_move_line.read(cr, uid, line_ids, ['debit', 'credit'], context=context)
                if abs(lines[1]['debit'] - lines[0]['credit']) < 0.001 and abs(lines[0]['debit'] - lines[1]['credit']) < 0.001:
                    obj_move_line.reconcile(cr, uid, line_ids, context=context)

        return True

account_invoice()

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    def validate_picking(self, cr, uid, order_id, context=None):
        so_name = self.pool.get('sale.order').read(cr, uid, order_id, ['name'])['name']
        picking_id = self.search(cr, uid, [('origin', '=', so_name)])[0]
        picking = self.browse(cr, uid, picking_id)
        self.force_assign(cr, uid, [picking_id])
        partial_data = {}
        for move in picking.move_lines:
            partial_data["move" + str(move.id)] = {'product_qty': move.product_qty}
        self.do_partial(cr, uid, [picking_id], partial_data)
        return True
        
    def validate_manufactoring_order(self, cr, uid, order_id, context=None): #we do not create class mrp.production to avoid dependence with the module mrp
        if context == None:
            context = {}
        wf_service = netsvc.LocalService("workflow")
        so_name = self.pool.get('sale.order').read(cr, uid, order_id, ['name'])['name']
        mrp_prod_obj = self.pool.get('mrp.production')
        mrp_product_produce_obj = self.pool.get('mrp.product.produce')
        production_ids = mrp_prod_obj.search(cr, uid, [('origin', '=', so_name)])
        for production in mrp_prod_obj.browse(cr, uid, production_ids):
            mrp_prod_obj.force_production(cr, uid, [production.id])
            wf_service.trg_validate(uid, 'mrp.production', production.id, 'button_produce', cr)
            print context
            context.update({'active_model': 'mrp.production', 'active_ids': [production.id], 'search_default_ready': 1, 'active_id': production.id})
            print context
            produce = mrp_product_produce_obj.create(cr, uid, {'mode': 'consume_produce', 'product_qty': production.product_qty}, context)
            print produce
            mrp_product_produce_obj.do_produce(cr, uid, [produce], context)
        return True
        
stock_picking()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
