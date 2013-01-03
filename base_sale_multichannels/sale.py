# -*- encoding: utf-8 -*-
#########################################################################
#                                                                       #
# Copyright (C) 2009  Raphaël Valyi                                     #
# Copyright (C) 2010-2011 Akretion Sébastien BEAU                       #
#                                        <sebastien.beau@akretion.com>  #
# Copyright (C) 2011-2012 Camptocamp Guewen Baconnier                   #
# Copyright (C) 2011 by Openlabs Technologies & Consulting (P) Limited  #
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

from openerp.osv.orm import Model
from openerp.osv import fields
from openerp.osv.osv import except_osv
import pooler
from sets import Set as set
import netsvc
from tools.translate import _
import time
import decimal_precision as dp
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from base_external_referentials.external_osv import ExternalSession
from base_external_referentials.decorator import open_report
from base_external_referentials.decorator import catch_error_in_report

#TODO use external_session.logger when it's posible
import logging
_logger = logging.getLogger(__name__)


class StockPicking(Model):
    '''Add a flag for marking picking as exported'''
    _inherit = 'stock.picking'

    _columns = {
        'exported_to_magento': fields.boolean('Exported to Magento',
            readonly=True),
    }


class external_shop_group(Model):
    _name = 'external.shop.group'
    _description = 'External Referential Shop Group'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'referential_id': fields.many2one('external.referential', 'Referential', select=True,
                                                                             ondelete='cascade'),
        'shop_ids': fields.one2many('sale.shop', 'shop_group_id', 'Sale Shops'),
    }


    def _get_default_import_values(self, cr, uid, external_session, **kwargs):
        return {'referential_id' : external_session.referential_id.id}


class external_referential(Model):
    _inherit = 'external.referential'

    _columns = {
        'shop_group_ids': fields.one2many('external.shop.group', 'referential_id', 'Sub Entities'),
    }



class ExternalShippingCreateError(Exception):
     """
      This error has to be raised when we tried to create a stock.picking on
      the external referential and the external referential has failed
      to create it. It must be raised only when we are SURE that the
      external referential will never be able to create it!
     """
     pass


class sale_shop(Model):
    _inherit = "sale.shop"

    def _get_exportable_category_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for shop in self.browse(cr, uid, ids, context=context):
            res[shop.id] = set()
            for category in shop.exportable_root_category_ids:
                res[shop.id] = res[shop.id].union(set(self.pool.get('product.category')._get_recursive_children_ids(cr, uid, [category.id], "", [], context)[category.id]))
            res[shop.id] = list(res[shop.id])
        return res

    def _get_exportable_product_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for shop in self.read(cr, uid, ids, ['exportable_category_ids'], context=context):
            all_categories = shop['exportable_category_ids']

            # If product_m2mcategories module is installed search in main category
            # and extra categories. If not, only in main category
            cr.execute('select * from ir_module_module where name=%s and state=%s',
                                                            ('product_m2mcategories','installed'))
            if cr.fetchone():
                res[shop['id']] = self.pool.get("product.product").search(cr, uid, ['|',
                        ('categ_id', 'in', all_categories),('categ_ids', 'in', all_categories)])
            else:
                res[shop['id']] = self.pool.get("product.product").search(cr, uid,
                                                            [('categ_id', 'in', all_categories)])
        return res

    def _get_referential_id(self, cr, uid, ids, name, args, context=None):
        res = {}
        for shop in self.browse(cr, uid, ids, context=context):
            if shop.shop_group_id:
                res[shop.id] = shop.shop_group_id.referential_id.id
            else:
                res[shop.id] = shop.referential_integer_id
        return res

    def _get_shop_from_shop_group(self, cr, uid, ids, context=None):
        return self.pool.get('sale.shop').search(cr, uid, [('shop_group_id', 'in', ids)], context=context)

    def _set_referential_id(self, cr, uid, id, name, value, arg, context=None):
        shop = self.browse(cr, uid, id, context=context)
        if shop.shop_group_id:
            raise except_osv(_("User Error"), _("You can not change the referential of this shop, please change the referential of the shop group!"))
        else:
            self.write(cr, uid, id, {'referential_integer_id': value}, context=context)
        return True

    def _get_shop_ids(self, cr, uid, ids, context=None):
        shop_ids=[]
        for group in self.pool.get('external.shop.group').browse(cr, uid, ids, context=context):
            shop_ids += [shop.id for shop in group.shop_ids]
        return shop_ids

    def _get_stock_field_id(self, cr, uid, context=None):
        if self.pool.get('ir.module.module').search(cr, uid, [
                    ['name', '=', 'stock_available_immediately'],
                    ['state', 'in', ['installed', 'to upgrade']],
                                            ], context=context):
            stock_field = 'immediately_usable_qty'
        else:
            stock_field = 'virtual_available'

        field_ids = self.pool.get('ir.model.fields').search(
            cr, uid,
            [('model', '=', 'product.product'),
             ('name', '=', stock_field)],
            context=context)
        return field_ids[0]

    #Depending of the e-commerce solution use you can have one or more root category
    #If you need only one the value will be stored in the exportable_root_category_ids fields
    def _get_rootcategory(self, cr, uid, ids, name, value, context=None):
        res = {}
        for shop in self.browse(cr, uid, ids, context):
            res[shop.id] = shop.exportable_root_category_ids and shop.exportable_root_category_ids[0].id or False
        return res

    def _set_rootcategory(self, cr, uid, id, name, value, fnct_inv_arg, context=None):
        return self.write(cr, uid, id, {'exportable_root_category_ids': [(6,0,[value])]}, context=context)

    def _get_referential_type_name(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for shop in self.browse(cr, uid, ids):
            if shop.referential_id:
                result[shop.id] = shop.referential_id.type_id.name
            else:
                result[shop.id] = False
        return result

    _columns = {
        'exportable_category_ids': fields.function(_get_exportable_category_ids, type='many2many', relation="product.category", string='Exportable Categories'),
        'exportable_root_category_ids': fields.many2many('product.category', 'shop_category_rel', 'categ_id', 'shop_id', 'Exportable Root Categories'),
        'exportable_root_category_id':fields.function(_get_rootcategory, fnct_inv = _set_rootcategory, type="many2one", relation="product.category", string="Root Category"),
        'exportable_product_ids': fields.function(_get_exportable_product_ids, type='many2many', relation="product.product", string='Exportable Products'),
        'shop_group_id': fields.many2one('external.shop.group', 'Shop Group', ondelete='cascade'),
        'last_inventory_export_date': fields.datetime('Last Inventory Export Time'),
        'last_images_export_date': fields.datetime('Last Images Export Time'),
        'last_update_order_export_date' : fields.datetime('Last Order Update  Time'),
        'last_products_export_date' : fields.datetime('Last Product Export Time'),
        'last_special_products_export_date' : fields.datetime('Last Special Product Export Time'),
        'last_category_export_date' : fields.datetime('Last Category Export Time'),
        'referential_id': fields.function(_get_referential_id,
            fnct_inv=_set_referential_id, type='many2one',
            relation='external.referential', string='External Referential', store={
                'sale.shop': (lambda self, cr, uid, ids, c={}: ids, ['referential_integer_id', 'shop_group_id'], 10),
                'external.shop.group': (_get_shop_from_shop_group, ['referential_id'], 20),
                }),
        'referential_integer_id': fields.integer('Referential Integer ID'),
        'is_tax_included': fields.boolean('Prices Include Tax', help="Does the external system work with Taxes Inclusive Prices ?"),
        'sale_journal': fields.many2one('account.journal', 'Sale Journal'),
        'order_prefix': fields.char('Order Prefix', size=64),
        'default_payment_method_id': fields.many2one('payment.method', 'Payment Method'),
        'default_language': fields.many2one('res.lang', 'Default Language'),
        'default_fiscal_position': fields.many2one('account.fiscal.position', 'Default Fiscal Position'),
        'default_customer_account': fields.many2one('account.account', 'Default Customer Account'),
        'default_customer_lang': fields.many2one('res.lang', 'Default Customer Language'),
        'auto_import': fields.boolean('Automatic Import'),
        'address_id':fields.many2one('res.partner.address', 'Address'),
        'website': fields.char('Website', size=64),
        'image':fields.binary('Image', filters='*.png,*.jpg,*.gif'),
        'use_external_tax': fields.boolean(
            'Use External Taxes',
            help="If activated, the external taxes will be applied.\n"
                 "If not activated, OpenERP will compute them "
                 "according to default values and fiscal positions."),
        'import_orders_from_date': fields.datetime('Only created after'),
        'check_total_amount': fields.boolean('Check Total Amount', help="The total amount computed by OpenERP should match with the external amount, if not the sale order can not be confirmed."),
        'type_name': fields.function(_get_referential_type_name, type='char', string='Referential type',
                store={
                'sale.shop': (lambda self, cr, uid, ids, c={}: ids, ['referential_id', 'shop_group_id'],10)}),
        'product_stock_field_id': fields.many2one(
            'ir.model.fields',
            string='Stock Field',
            domain="[('model', 'in', ['product.product', 'product.template']),"
                   " ('ttype', '=', 'float')]",
            help="Choose the field of the product which will be used for "
                 "stock inventory updates.\nIf empty, Quantity Available "
                 "is used"),
    }

    _defaults = {
        'payment_default_id': 1, #required field that would cause trouble if not set when importing
        'auto_import': True,
        'use_external_tax': True,
        'product_stock_field_id': _get_stock_field_id,
    }

    def init_context_before_exporting_resource(self, cr, uid, external_session, object_id, resource_name, context=None):
        context = super(sale_shop, self).init_context_before_exporting_resource(cr, uid, external_session, object_id, resource_name, context=context)
        context['pricelist'] = external_session.sync_from_object.get_pricelist(context=context)
        return context

    def get_pricelist(self, cr, uid, id, context=None):
        if isinstance(id, list):
            id=id[0]
        shop = self.browse(cr, uid, id, context=context)
        if shop.pricelist_id:
            return shop.pricelist_id.id
        else:
            return self.pool.get('product.pricelist').search(cr, uid, [('type', '=', 'sale'), ('active', '=', True)], context=context)[0]

    def export_catalog(self, cr, uid, ids, context=None):
        if context is None: context={}
        self.export_resources(cr, uid, ids, 'product.category', context=context)
        # In various e-commerce system product can depend of other products
        # So the simple product (with no dependency) are exported in priority
        # Then the special product (with dependency) are exported at the end
        context['export_product'] = 'simple'
        self.export_resources(cr, uid, ids, 'product.product', context=context)
        context['export_product'] = 'special'
        self.export_resources(cr, uid, ids, 'product.product', context=context)
        #Export Images
        self.export_resources(cr, uid, ids, 'product.images', context=context)

        #TODO export link
        #TODO update the last date
        #I don't know where it's the best to update it here or in the export functions
        #take care about concurent write with different cursor


        return True

    def export_inventory(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for shop in self.browse(cr, uid, ids):
            external_session = ExternalSession(shop.referential_id, shop)
            self._export_inventory(cr, uid, external_session, ids, context=context)
        return True

    def _get_product_ids_for_stock_to_export(self, cr, uid, shop, context=None):
        return [product.id for product in shop.exportable_product_ids]

    def _export_inventory(self, cr, uid, external_session, ids, context=None):
        shop = external_session.sync_from_object
        stock_move_obj = self.pool.get('stock.move')
        for shop in self.browse(cr, uid, ids):
            external_session = ExternalSession(shop.referential_id, shop)

            product_ids = self._get_product_ids_for_stock_to_export(cr, uid, shop, context=context)

            if shop.last_inventory_export_date:
                # we do not exclude canceled moves because it means
                # some stock levels could have increased since last export
                recent_move_ids = stock_move_obj.search(
                    cr, uid,
                    [('write_date', '>', shop.last_inventory_export_date),
                     ('product_id', 'in', product_ids),
                     ('product_id.type', '!=', 'service'),
                     ('state', '!=', 'draft')],
                    context=context)
            else:
                recent_move_ids = stock_move_obj.search(
                    cr, uid,
                    [('product_id', 'in', product_ids)],
                    context=context)

            recent_moves = stock_move_obj.browse(
                cr, uid, recent_move_ids, context=context)

            product_ids = [move.product_id.id
                           for move
                           in recent_moves
                           if move.product_id.state != 'obsolete']
            product_ids = list(set(product_ids))
            external_session.logger.info('Export Stock for %s products' %len(product_ids))
            self.pool.get('product.product').export_inventory(
                    cr, uid, external_session, product_ids, context=context)
            shop.write({'last_inventory_export_date':
                            time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def import_catalog(self, cr, uid, ids, context):
        #TODO import categories, then products
        raise except_osv(_("Not Implemented"), _("Not Implemented in abstract base module!"))

    def import_orders(self, cr, uid, ids, context=None):
        self.import_resources(cr, uid, ids, 'sale.order', context=context)
        return True

    def check_need_to_update(self, cr, uid, ids, context=None):
        """ This function will update the order status in OpenERP for
        the order which are in the state 'need to update' """
        for shop in self.browse(cr, uid, ids, context=context):
            external_session = ExternalSession(shop.referential_id, shop)
            so_obj = self.pool.get('sale.order')
            orders_to_update = so_obj.search(cr, uid,
                    [('need_to_update', '=', True),
                     ('shop_id', '=', shop.id)],
                    context=context)
            so_obj._check_need_to_update(cr, uid, external_session, orders_to_update, context=context)
        return False

    def _update_order_query(self, cr, uid, shop, context=None):
        req = """
            SELECT ir_model_data.res_id, ir_model_data.name
                FROM sale_order
                INNER JOIN ir_model_data ON sale_order.id = ir_model_data.res_id
                WHERE ir_model_data.model='sale.order' AND sale_order.shop_id=%s
                    AND ir_model_data.referential_id NOTNULL
        """
        params = (shop.id,)
        if shop.last_update_order_export_date:
            req += "AND sale_order.update_state_date > %s"
            params = (shop.id, shop.last_update_order_export_date)
        return req, params

    def update_orders(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for shop in self.browse(cr, uid, ids):
            external_session = ExternalSession(shop.referential_id, shop)
            #get all orders, which the state is not draft and the date of modification is superior to the last update, to exports
            cr.execute(*self._update_order_query(cr, uid, shop, context=context))
            results = cr.fetchall()
            for result in results:
                ids = self.pool.get('sale.order').search(cr, uid, [('id', '=', result[0])])
                if ids:
                    id = ids[0]
                    order = self.pool.get('sale.order').browse(cr, uid, id, context)
                    order_ext_id = result[1].split('sale_order/')[1]
                    res = self.update_shop_orders(cr, uid, external_session, order, order_ext_id, context)
                    if res:
                        external_session.logger.info(_("Successfully updated order with OpenERP id %s and ext id %s in external sale system") % (id, order_ext_id))
            self.pool.get('sale.shop').write(cr, uid, shop.id, {'last_update_order_export_date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return False

    def export_shop_partners(self, cr, uid, ids, context=None):
        if context is None: context={}
        self.export_resources(cr, uid, ids, 'res.partner', context=context)
        return True

    def update_shop_orders(self, cr, uid, external_session, order, ext_id, context):
        raise except_osv(_("Not Implemented"), _("Not Implemented in abstract base module!"))

    def _export_shipping_query(self, cr, uid, shop, context=None):
        query = """
        SELECT stock_picking.id AS picking_id,
               sale_order.id AS order_id,
               count(pickings.id) AS picking_number
        FROM stock_picking
        LEFT JOIN sale_order
                  ON sale_order.id = stock_picking.sale_id
        LEFT JOIN stock_picking as pickings
                  ON (sale_order.id = pickings.sale_id
                      AND pickings.type='out'
                      AND pickings.state!='cancel')
        LEFT JOIN ir_model_data
                  ON stock_picking.id = ir_model_data.res_id
                  AND ir_model_data.model = 'stock.picking'
        LEFT JOIN delivery_carrier
                  ON delivery_carrier.id = stock_picking.carrier_id
        WHERE sale_order.shop_id = %(shop_id)s
              AND ir_model_data.res_id ISNULL
              AND stock_picking.state = 'done'
              AND stock_picking.type = 'out'
              AND NOT stock_picking.do_not_export
              AND (NOT delivery_carrier.export_needs_tracking
                   OR stock_picking.carrier_tracking_ref IS NOT NULL)
        GROUP BY stock_picking.id,
                 sale_order.id,
                 delivery_carrier.export_needs_tracking,
                 stock_picking.carrier_tracking_ref,
                 stock_picking.backorder_id
        ORDER BY sale_order.id ASC,
                 COALESCE(stock_picking.backorder_id, NULL, 0) ASC"""
        params = {'shop_id': shop.id}
        return query, params

    def export_shipping(self, cr, uid, ids, context):
        picking_obj = self.pool.get('stock.picking')
        for shop in self.browse(cr, uid, ids):
            cr.execute(*self._export_shipping_query(
                            cr, uid, shop, context=context))
            results = cr.dictfetchall()
            if not results:
                _logger.info("There is no shipping to export for the shop '%s' to the external referential", shop.name)
                continue
            context['conn_obj'] = shop.referential_id.external_connection()


            picking_cr = pooler.get_db(cr.dbname).cursor()
            try:
                for result in results:
                    picking_id = result['picking_id']

                    if result["picking_number"] == 1:
                        picking_type = 'complete'
                    else:
                        picking_type = 'partial'

                    ext_shipping_id = False
                    try:
                        ext_shipping_id = picking_obj.create_ext_shipping(
                            picking_cr, uid, picking_id, picking_type,
                            shop.referential_id.id, context)
                    except ExternalShippingCreateError, e:
                        # when the creation has failed on the external
                        # referential and we know that we can never
                        # create it, we flag it as do_not_export
                        # ExternalShippingCreateError raising has to be
                        # correctly handled by create_ext_shipping()
                        picking_obj.write(
                            picking_cr, uid,
                            picking_id,
                            {'do_not_export': True},
                            context=context)

                    if ext_shipping_id:
                        picking_obj.create_external_id_vals(
                            picking_cr,
                            uid,
                            picking_id,
                            ext_shipping_id,
                            shop.referential_id.id,
                            context=context)
                        _logger.info("Successfully creating shipping with OpenERP id %s and ext id %s in external sale system", result["picking_id"], ext_shipping_id)
                    picking_cr.commit()
            finally:
                picking_cr.close()
        return True

    def export_invoices(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        for shop in self.browse(cr, uid, ids, context=None):
            external_session = ExternalSession(shop.referential_id, shop)
            invoice_ids = self.get_invoice_to_export(cr, uid, shop.id, context=context)
            if not invoice_ids:
                external_session.logger.info("There is no invoice to export for the shop '%s' to the external referential" % (shop.name,))
            for invoice_id in invoice_ids:
                self.pool.get('account.invoice')._export_one_resource(cr, uid, external_session, invoice_id, context=context)
        return True

    def get_invoice_to_export(self, cr, uid, shop_id, context=None):
        shop = self.browse(cr, uid, shop_id, context=context)
        cr.execute(*self._export_invoice_query(cr, uid, shop, context=context))
        results = cr.dictfetchall()
        return [res['invoice_id'] for res in results]

    def _export_invoice_query(self, cr, uid, shop, context=None):
        query = """
        SELECT account_invoice.id AS invoice_id
        FROM account_invoice
        LEFT JOIN ir_model_data
                  ON account_invoice.id = ir_model_data.res_id
                  AND ir_model_data.model = 'account.invoice'
                  AND referential_id = %(referential_id)s
        WHERE shop_id = %(shop_id)s
              AND ir_model_data.res_id ISNULL
              AND account_invoice.state in ('paid', 'open')
              AND NOT account_invoice.do_not_export
        """
        params = {'shop_id': shop.id, 'referential_id': shop.referential_id.id}
        return query, params

sale_shop()


class sale_order(Model):
    _inherit = "sale.order"

    _columns = {
        'need_to_update': fields.boolean('Need To Update'),
        'ext_total_amount': fields.float(
            'Origin External Amount',
            digits_compute=dp.get_precision('Sale Price'),
            readonly=True),
        'ext_total_amount_tax': fields.float(
            'Origin External Tax Amount',
            digits_compute=dp.get_precision('Sale Price'),
            readonly=True),
        'referential_id': fields.related(
                    'shop_id', 'referential_id',
                    type='many2one', relation='external.referential',
                    string='External Referential'),
        'update_state_date': fields.datetime('Update State Date'),
        'shipping_tax_amount': fields.dummy(string = 'Shipping Taxe Amount'),
        'shipping_amount_tax_excluded': fields.dummy(string = 'Shipping Price Tax Exclude'),
        'shipping_amount_tax_included': fields.dummy(string = 'Shipping Price Tax Include'),
    }

    _defaults = {
        'need_to_update': False,
    }

    def write(self, cr, uid, ids, vals, context=None):
        if 'state' in vals:
            vals['update_state_date'] = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return super(sale_order, self).write(cr, uid, ids, vals, context=context)

    def _get_default_import_values(self, cr, uid, external_session, mapping_id=None, defaults=None, context=None):
        shop = False
        if external_session.sync_from_object._name == 'sale.shop':
            shop = external_session.sync_from_object
        elif context.get('sale_shop_id'):
            shop = self.pool.get('sale.shop').browse(cr, uid,  context['sale_shop_id'], context=context)
        if shop:
            if defaults is None: defaults = {}
            defaults.update({
                    'pricelist_id': shop.get_pricelist(context=context),
                    'shop_id': shop.id,
                    'fiscal_position': shop.default_fiscal_position.id,
                    'payment_method_id': shop.default_payment_method_id.id,
                    'company_id': shop.company_id.id,
            })
            #TODO we should avoid passing this parameter in the context
            #for now we new it for importing order from wizard correctly
            #refactor for V7
            context.update({
                    'use_external_tax': shop.use_external_tax,
                    'is_tax_included': shop.is_tax_included,
                })
        return defaults

    @open_report
    def _import_resources(self, cr, uid, external_session, defaults=None, method="search_then_read", context=None):
        if context is None: context={}
        shop = external_session.sync_from_object
        if shop:
            context.update({
                    'use_external_tax': shop.use_external_tax,
                    'is_tax_included': shop.is_tax_included,
                })
        return super(sale_order, self)._import_resources(cr, uid, external_session, defaults=defaults, method=method, context=context)


    def check_if_order_exist(self, cr, uid, external_session, resource, order_mapping=None, defaults=None, context=None):
        mapping_name = False
        for line in order_mapping['mapping_lines']:
            if line['internal_field'] == 'name':
                mapping_name = line
        if mapping_name:
            local_mapping = {1: {'mapping_lines': [mapping_name]}}
            vals = self._transform_one_resource(cr, uid, external_session,
                                        'from_external_to_openerp', resource,
                                        mapping=local_mapping,
                                        mapping_id=1,
                                        defaults=defaults,
                                        context=context)
            if vals.get('name'):
                exist_id = self.search(cr, uid, [['name', '=', vals['name']]], context=context)
                if exist_id:
                    external_session.logger.info("Sale Order %s already exist in OpenERP,"
                                                    "no need to import it again"%vals['name'])
                    return True

        return False

    @catch_error_in_report
    def _record_one_external_resource(self, cr, uid, external_session, resource, defaults=None,
                                                        mapping=None, mapping_id=None, context=None):
        mapping, mapping_id = self._init_mapping(cr, uid, external_session.referential_id.id,
                                            mapping=mapping, mapping_id=mapping_id, context=context)
        exist_id = self.check_if_order_exist(cr, uid, external_session, resource,
                                            order_mapping=mapping[mapping_id], defaults=defaults, context=context)
        if exist_id:
            return {}
        else:
            return super(sale_order, self)._record_one_external_resource(cr, uid, external_session, resource,
                                defaults=defaults, mapping=mapping, mapping_id=mapping_id, context=context)

    def _check_need_to_update(self, cr, uid, external_session, ids, context=None):
        """
        For each order, check in external system if it has been paid since last
        check. If so, it will launch the defined flow based on the
        payment type (validate order, invoice, ...)
        """
        for order in self.browse(cr, uid, ids, context=context):
            self._check_need_to_update_single(cr, uid, external_session, order, context=context)
        return True

    def _check_need_to_update_single(self, cr, uid, external_session, order, context=None):
        """Not implemented in this abstract module"""
        return True

    def _get_params_onchange_partner_id(self, cr, uid, vals, context=None):
        args = [
            'None',
            vals.get('partner_id'),
        ]
        return args, {}

    #I will probably extract this code in order to put it in a "glue" module
    def _get_params_onchange_address_id(self, cr, uid, vals, context=None):
        args = [
            None,
            vals.get('partner_invoice_id'),
            vals.get('partner_shipping_id'),
            vals.get('partner_id'),
        ]
        kwargs = {
            'shop_id': vals.get('shop_id'),
        }
        return args, kwargs

    def play_sale_order_onchange(self, cr, uid, vals, defaults=None, context=None):
        ir_module_obj= self.pool.get('ir.module.module')
        if ir_module_obj.search(cr, uid, [
                            ['name', '=', 'account_fiscal_position_rule_sale'],
                            ['state', 'in', ['installed', 'to upgrade']],
                                                            ], context=context):
            vals = self.call_onchange(cr, uid, 'onchange_partner_id', vals, defaults, context=context)
            vals = self.call_onchange(cr, uid, 'onchange_address_id', vals, defaults, context=context)
        else:
            vals = self.call_onchange(cr, uid, 'onchange_partner_id', vals, defaults, context=context)


        return vals

    def _merge_with_default_values(self, cr, uid, external_session, ressource, vals, sub_mapping_list, defaults=None, context=None):
        if vals.get('name'):
            shop = external_session.sync_from_object
            if shop.order_prefix:
                vals['name'] = '%s%s' %(shop.order_prefix, vals['name'])
        if context is None: context ={}
        if vals.get('payment_method_id'):
            payment_method = self.pool.get('payment.method').browse(cr, uid, vals['payment_method_id'], context=context)
            workflow_process = payment_method.workflow_process_id
            if workflow_process:
                vals['order_policy'] = workflow_process.order_policy
                vals['picking_policy'] = workflow_process.picking_policy
                vals['invoice_quantity'] = workflow_process.invoice_quantity
        # update vals with order onchange in order to compute taxes
        vals = self.play_sale_order_onchange(cr, uid, vals, defaults=defaults, context=context)
        return super(sale_order, self)._merge_with_default_values(cr, uid, external_session, ressource, vals, sub_mapping_list, defaults=defaults, context=context)

    def oe_create(self, cr, uid, external_session, vals, resource, defaults, context):
        #depending of the external system the contact address can be optionnal
        vals = self._convert_special_fields(cr, uid, vals, external_session.referential_id.id, context=context)
        if not vals.get('partner_order_id'):
            vals['partner_order_id'] = vals['partner_invoice_id']
        if not vals.get('partner_shipping_id'):
            vals['partner_shipping_id'] = vals['partner_invoice_id']
        order_id = super(sale_order, self).oe_create(cr, uid, external_session, vals, resource, defaults, context)
        self.paid_and_update(cr, uid, external_session, order_id, resource, context=context)
        return order_id

    def paid_and_update(self, cr, uid, external_session, order_id, resource, context=None):
        wf_service = netsvc.LocalService("workflow")
        paid = self.create_external_payment(cr, uid, external_session, order_id, resource, context)
        order = self.browse(cr, uid, order_id, context=context)
        validate_order = order.workflow_process_id.validate_order
        if validate_order == 'always' or validate_order == 'if_paid' and paid:
            try:
                wf_service.trg_validate(uid, 'sale.order', order.id, 'order_confirm', cr)
            except:
                raise
                #What we should do?? creating the order but not validating it???
                #Maybe setting a special flag can be a good solution? with a retry method?
            return True

        elif validate_order == 'if_paid' and order.payment_method_id.automatic_update:
            days_before_order_cancel = order.workflow_process_id.days_before_order_cancel or 30
            order_date = datetime.strptime(order.date_order, DEFAULT_SERVER_DATE_FORMAT)
            order_cancel_date = order_date + relativedelta(days=days_before_order_cancel)
            if order.state == 'draft' and order_cancel_date < datetime.now():
                wf_service.trg_validate(uid, 'sale.order', order.id, 'cancel', cr)
                self.write(cr, uid, order.id, {'need_to_update': False})
                self.log(cr, uid, order.id, ("order %s canceled in OpenERP because older than % days"
                                     "and still not confirmed") % (order.id, days_before_order_cancel))
                #TODO eventually call a trigger to cancel the order in the external system too
                external_session.logger.info(("order %s canceled in OpenERP because older than % days and "
                                "still not confirmed") %(order.id, days_before_order_cancel))
            else:
                self.write(cr, uid, order_id, {'need_to_update': True}, context=context)
        return False

    def create_external_payment(self, cr, uid, external_session, order_id, resource, context):
        """
        Fonction that will create a payment from the external resource
        """
        vals = self._get_payment_information(cr, uid, external_session, order_id, resource, context=context)
        if vals.get('paid'):
            if not vals.get('journal_id'):
                external_session.logger.warning(_("Not journal found for payment method %s. Can not create payment")%vals['payment_method'])
                vals['paid'] = False
            else:
                self.pay_sale_order(cr, uid, order_id, vals['journal_id'], vals['amount'], vals['date'], context=context)
        return vals.get('paid')

    def _get_payment_information(self, cr, uid, external_session, order_id, resource, context=None):
        """
        Function that will return the information in order to create the payment
        """
        vals = {}
        sale = self.browse(cr, uid, order_id, context=context)
        vals['payment_method'] = sale.payment_method_id.name
        vals['journal_id'] = sale.payment_method_id.journal_id and sale.payment_method_id.journal_id.id
        vals['date'] = sale.date_order
        return vals

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sale order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) lines: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        vals = super(sale_order, self)._prepare_invoice(cr, uid, order, lines, context=context)
        if order.shop_id.sale_journal:
            vals['journal_id'] = order.shop_id.sale_journal.id
        vals['shop_id'] = order.shop_id.id
        return vals

    def _prepare_order_picking(self, cr, uid, order, context=None):
        vals = super(sale_order, self)._prepare_order_picking(cr, uid, order, context=context)
        vals['shop_id'] = order.shop_id.id
        return vals

    def oe_update(self, cr, uid, external_session, existing_rec_id, vals, resource, defaults, context=None):
        '''Not implemented in this abstract module, if it's not implemented in your module it will raise an error'''
        # Explication :
        # sometime customer can do ugly thing like renamming a sale_order and try to reimported it,
        # sometime openerp run two scheduler at the same time, or the customer launch two openerp at the same time
        # or the external system give us again an already imported order
        # As the update of an existing order (this is not the update of the status but the update of the line, the address...)
        # is not supported by base_sale_multichannels and also not in magentoerpconnect.
        # It's better to don't allow this feature to avoid hidding a problem.
        # It's better to have the order not imported and to know it than having order with duplicated line.
        if not (context and context.get('oe_update_supported', False)):
            #TODO found a clean solution to raise the except_osv error in the try except of the function import_with_try
            raise except_osv(_("Not Implemented"), _(("The order with the id %s try to be updated from the external system."
                                " This feature is not supported. Maybe the import try to reimport an existing sale order"%(existing_rec_id,))))
        return super(sale_order, self).oe_update(cr, uid, external_session, existing_rec_id, vals, resource, defaults, context=context)

    def _convert_special_fields(self, cr, uid, vals, referential_id, context=None):
        """
        Convert the special 'fake' field into an order line
        special field are :
        - shipping amount and shipping_tax_rate
        - cash_on_delivery and cash_on_delivery_taxe_rate
        - gift_certificates

        :param dict vals : values of the sale order to create
        :param int referential_id : external referential id
        :return: the value for the sale order with the special field converted
        :rtype: dict
        """
        def check_key(keys):
            return len(set([
                        'shipping_amount_tax_excluded',
                        'shipping_amount_tax_included',
                        'shipping_tax_amount'])
                    & set(keys)) >= 2

        for line in vals['order_line']:
            for field in ['shipping_amount_tax_excluded','shipping_amount_tax_included', 'shipping_tax_amount']:
                if field in line[2]:
                    vals[field] = vals.get(field, 0.0) + line[2][field]
                    del line[2][field]

        if not 'shipping_tax_rate' in vals and check_key(vals.keys()):
            if not 'shipping_amount_tax_excluded' in vals:
                vals['shipping_amount_tax_excluded'] = vals['shipping_amount_tax_included'] - vals['shipping_tax_amount']
            elif not 'shipping_tax_amount' in vals:
                vals['shipping_tax_amount'] = vals['shipping_amount_tax_included'] - vals['shipping_amount_tax_excluded']
            vals['shipping_tax_rate'] = vals['shipping_amount_tax_excluded'] and \
                            vals['shipping_tax_amount'] / vals['shipping_amount_tax_excluded'] or 0
            del vals['shipping_tax_amount']
        for option in self._get_special_fields(cr, uid, context=context):
            vals = self._add_order_extra_line(cr, uid, vals, option, context=context)
        return vals


    def _get_special_fields(self, cr, uid, context=None):
        return [
            {
            'price_unit_tax_excluded' : 'shipping_amount_tax_excluded',
            'price_unit_tax_included' : 'shipping_amount_tax_included',
            'tax_rate_field' : 'shipping_tax_rate',
            'product_ref' : ('base_sale_multichannels', 'product_product_shipping'),
            },
            {
            'tax_rate_field' : 'cash_on_delivery_taxe_rate',
            'price_unit_tax_excluded' : 'cash_on_delivery_amount_tax_excluded',
            'price_unit_tax_included' : 'cash_on_delivery_amount_tax_included',
            'product_ref' : ('base_sale_multichannels', 'product_product_cash_on_delivery'),
            },
            {
            'price_unit_tax_excluded' : 'gift_certificates_amount', #gift certificate doesn't have any tax
            'price_unit_tax_included' : 'gift_certificates_amount',
            'product_ref' : ('base_sale_multichannels', 'product_product_gift'),
            'code_field': 'gift_certificates_code',
            'sign': -1,
            },
        ]

    def _add_order_extra_line(self, cr, uid, vals, option, context):
        """ Add or substract amount on order as a separate line item with single quantity for each type of amounts like :
        shipping, cash on delivery, discount, gift certificates...

        :param dict vals: values of the sale order to create
        :param option: dictionnary of option for the special field to process
        """
        if context is None: context={}
        sign = option.get('sign', 1)
        if context.get('is_tax_included') and vals.get(option['price_unit_tax_included']):
            price_unit = vals.pop(option['price_unit_tax_included']) * sign
        elif vals.get(option['price_unit_tax_excluded']):
            price_unit = vals.pop(option['price_unit_tax_excluded']) * sign
        else:
            for key in ['price_unit_tax_excluded', 'price_unit_tax_included', 'tax_rate_field']:
                if option.get(key) and option[key] in vals:
                    del vals[option[key]]
            return vals #if there is not price, we have nothing to import

        model_data_obj = self.pool.get('ir.model.data')
        model, product_id = model_data_obj.get_object_reference(cr, uid, *option['product_ref'])
        product = self.pool.get('product.product').browse(cr, uid, product_id, context)

        extra_line = {
                        'product_id': product.id,
                        'name': product.name,
                        'product_uom': product.uom_id.id,
                        'product_uom_qty': 1,
                        'price_unit': price_unit,
                    }

        extra_line = self.pool.get('sale.order.line').play_sale_order_line_onchange(cr, uid, extra_line, vals, vals['order_line'], context=context)
        if context.get('use_external_tax') and option.get('tax_rate_field'):
            tax_rate = vals.pop(option['tax_rate_field'])
            if tax_rate:
                line_tax_id = self.pool.get('account.tax').get_tax_from_rate(cr, uid, tax_rate, context.get('is_tax_included'), context=context)
                if not line_tax_id:
                    raise except_osv(_('Error'), _('No tax id found for the rate %s with the tax include = %s')%(tax_rate, context.get('is_tax_included')))
                extra_line['tax_id'] = [(6, 0, [line_tax_id])]
            else:
                extra_line['tax_id'] = False
        if not option.get('tax_rate_field'):
            del extra_line['tax_id']
        ext_code_field = option.get('code_field')
        if ext_code_field and vals.get(ext_code_field):
            extra_line['name'] = "%s [%s]" % (extra_line['name'], vals[ext_code_field])
        vals['order_line'].append((0, 0, extra_line))
        return vals

class sale_order_line(Model):
    _inherit='sale.order.line'

    _columns = {
        'ext_product_ref': fields.char('Product Ext Ref',
                            help="This is the original external product reference", size=256),
        'shipping_tax_amount': fields.dummy(string = 'Shipping Taxe Amount'),
        'shipping_amount_tax_excluded': fields.dummy(string = 'Shipping Price Tax Exclude'),
        'shipping_amount_tax_included': fields.dummy(string = 'Shipping Price Tax Include'),
        'ext_ref_line': fields.char('Ext. Ref Line', size=64,
                help='Unique order line id delivered by external application'),
    }

    def _get_params_product_id_change(self, cr, uid, line, parent_data, previous_lines, context=None):
        args = [
            None,
            parent_data.get('pricelist_id'),
            line.get('product_id')
        ]
        kwargs ={
            'qty': float(line.get('product_uom_qty')),
            'uom': line.get('product_uom'),
            'qty_uos': float(line.get('product_uos_qty') or line.get('product_uom_qty')),
            'uos': line.get('product_uos'),
            'name': line.get('name'),
            'partner_id': parent_data.get('partner_id'),
            'lang': False,
            'update_tax': True,
            'date_order': parent_data.get('date_order'),
            'packaging': line.get('product_packaging'),
            'fiscal_position': parent_data.get('fiscal_position'),
            'flag': False,
            'context': context,
        }
        return args, kwargs

    def play_sale_order_line_onchange(self, cr, uid, line, parent_data, previous_lines, defaults=None, context=None):
        original_line = line.copy()
        if not context.get('use_external_tax') and 'tax_id' in line:
            del line['tax_id']
        line = self.call_onchange(cr, uid, 'product_id_change', line, defaults=defaults, parent_data=parent_data, previous_lines=previous_lines, context=context)
        #TODO all m2m should be mapped correctly
        if context.get('use_external_tax'):
            #if we use the external tax and the onchange have added a taxe, 
            #them we remove it.
            #Indeed we have to make the difference between a real tax_id
            #imported and a default value set by the onchange
            if not 'tax_id' in original_line and 'tax_id' in line:
                del line['tax_id']
        elif line.get('tax_id'):
            line['tax_id'] = [(6, 0, line['tax_id'])]
        return line

    def _transform_one_resource(self, cr, uid, external_session, convertion_type, resource, mapping, mapping_id,
                     mapping_line_filter_ids=None, parent_data=None, previous_result=None, defaults=None, context=None):
        if context is None: context={}
        line = super(sale_order_line, self)._transform_one_resource(cr, uid, external_session, convertion_type, resource,
                            mapping, mapping_id, mapping_line_filter_ids=mapping_line_filter_ids, parent_data=parent_data,
                            previous_result=previous_result, defaults=defaults, context=context)

        if context.get('is_tax_included') and 'price_unit_tax_included' in line:
            line['price_unit'] = line['price_unit_tax_included']
        elif 'price_unit_tax_excluded' in line:
            line['price_unit']  = line['price_unit_tax_excluded']

        line = self.play_sale_order_line_onchange(cr, uid, line, parent_data, previous_result,
                                                                        defaults, context=context)
        if context.get('use_external_tax'):
            if not 'tax_id' in line and line.get('tax_rate'):
                line_tax_id = self.pool.get('account.tax').get_tax_from_rate(cr, uid, line['tax_rate'], context.get('is_tax_included', False), context=context)
                if not line_tax_id:
                    raise except_osv(_('Error'), _('No tax id found for the rate %s with the tax include = %s')%(line['tax_rate'], context.get('is_tax_included')))
                line['tax_id'] = [(6, 0, [line_tax_id])]
            else:
                line['tax_id'] = False
        return line

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
