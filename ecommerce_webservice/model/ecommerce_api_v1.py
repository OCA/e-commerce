# -*- coding: utf-8 -*-
import sys
import time
import traceback
from functools import wraps

import sql_db
import netsvc
import openerp
from openerp.osv import orm
from openerp import SUPERUSER_ID
from openerp.tools.translate import _

class ecommerce_api_v1(orm.AbstractModel):
    _name = 'ecommerce.api.v1'

    def _shop_logging(method):
        @wraps(method)
        def wrapped(self, cr, uid, shop_identifier, *args, **kwargs):
            context = None
            if context in kwargs:
                context = kwargs['context']
            shop = self._find_shop(cr, SUPERUSER_ID, shop_identifier, context)
            internal_uid = shop.internal_user_id.id
            try:
                values = {
                    'shop_id': shop.id,
                    'external_uid': uid,
                    'method': method.func_name,
                    # serialize args before calling as they might get modified
                    'args': "args:\n%s\n\nkwargs:\n%s" % (args, kwargs),
                    }
                result = method(self, cr, internal_uid, shop, *args, **kwargs)
            except:
                exc_info = sys.exc_info()
                values.update({
                    'state': 'failure',
                    'exc_info': traceback.format_exc(exc_info),
                    })
                raise exc_info[0], exc_info[1], exc_info[2]
            else:
                values['state'] = 'success'
                if not shop.logs_all_on_success:
                    values.pop('args')
                return result
            finally:
                if shop.enable_logs:
                    new_cr = sql_db.db_connect(cr.dbname).cursor()
                    self.pool['ecommerce.api.log'].create(new_cr, SUPERUSER_ID, values, context)
                    new_cr.commit()
                    new_cr.close()
        return wrapped

    def _find_shop(self, cr, uid, shop_identifier, context=None):
        Shop = self.pool['ecommerce.api.shop']
        shops = Shop.search(cr, uid, [('shop_identifier', '=', shop_identifier)], context=context)
        if not shops:
            raise openerp.exceptions.AccessError(_('No shop found with identifier %s') % shop_identifier)
        shop = Shop.browse(cr, uid, shops[0], context=context)
        return shop

    def _update_vals_for_country_id(self, cr, uid, vals, context=None):
        if 'country' in vals:
            country_ids = self.pool['res.country'].name_search(cr, uid,
                    vals['country'], context=context)
            country_id = country_ids[0][0] if country_ids else False
            vals.pop('country')
            vals['country_id'] = country_id

    def _get_report(self, cr, uid, model, oid):
        ReportSpool = netsvc.ExportService._services['report']
        rid = ReportSpool.exp_report(cr.dbname, uid, model, [oid],
                {'model': model, 'id': oid, 'report_type':'pdf'})
        retry = 0
        while retry < 10:
            report = ReportSpool.exp_report_get(cr.dbname, uid, rid)
            if report['state']:
                break
            # there must be a better way
            time.sleep(min(.1 * 2 ** retry, 3))
            retry += 1
        return report['result']


    @_shop_logging
    def create_customer(self, cr, uid, shop, vals, context=None):
        self._update_vals_for_country_id(cr, uid, vals, context)
        vals.update({
            'customer': True,
            'type': 'default',
            'customer_eshop_id': shop.id, # link to shop.partner_ids
            })
        customer_id = self.pool['res.partner'].create(cr, uid, vals, context)
        return customer_id

    @_shop_logging
    def update_customer(self, cr, uid, shop, partner_id, vals, context=None):
        self._update_vals_for_country_id(cr, uid, vals, context)
        return self.pool['res.partner'].write(cr, uid, partner_id, vals, context=context)

    @_shop_logging
    def create_customer_address(self, cr, uid, shop, customer_id, vals, context=None):
        self._update_vals_for_country_id(cr, uid, vals, context)
        vals.update({
            'customer': True,
            'parent_id': customer_id,
            'address_eshop_id': shop.id, # link to shop.partner_ids
            })
        address_id = self.pool['res.partner'].create(cr, uid, vals, context)
        return address_id

    @_shop_logging
    def update_customer_address(self, cr, uid, shop, address_ids, vals, context=None):
        self._update_vals_for_country_id(cr, uid, vals, context)
        return self.pool['res.partner'].write(cr, uid, address_ids, vals, context=context)

    @_shop_logging
    def create_sale_order(self, cr, uid, shop, vals, context=None):
        SO = self.pool['sale.order']
        SOL = self.pool['sale.order.line']

        raw_order_line = vals.pop('order_line') if 'order_line' in vals else {}

        vals.update({
            'state': 'manual',
            'shop_id': shop.default_shop_id.id,
            'eshop_id': shop.id,
            })

        onchange_vals = {}
        if 'partner_id' in vals:
            ocv = SO.onchange_partner_id(cr, uid, None, vals['partner_id'], context=context)
            onchange_vals.update(ocv['value'])
        if 'shop_id' in vals:
            ocv = SO.onchange_shop_id(cr, uid, None, vals['shop_id'], context=context)
            onchange_vals.update(ocv['value'])

        # fields in vals prevail on fields returned by onchange
        for key in onchange_vals.keys():
            if key in vals:
                onchange_vals.pop(key)
        vals.update(onchange_vals)

        order_line = []
        for line in raw_order_line:
            onchange_vals = {}
            if 'product_id' in line:
                ocv = SOL.product_id_change(cr, uid, None,
                                           vals.get('pricelist_id'),
                                           line['product_id'],
                                           line.get('product_uom_qty'),
                                           line.get('product_uom'),
                                           line.get('product_uos_qty'),
                                           line.get('product_uos'),
                                           line.get('name'),
                                           vals['partner_id'],
                                           date_order=vals.get('date_order'),
                                           context=context)
                onchange_vals.update(ocv['value'])
            for key in onchange_vals.keys():
                if key in line:
                    onchange_vals.pop(key)
            line.update(onchange_vals)
            order_line.append([0, False, line])

        vals['order_line'] = order_line
        so_id = SO.create(cr, uid, vals, context=context)
        return so_id

    @_shop_logging
    def search_read_product_template(self, cr, uid, shop, domain,
            fields=None, offset=0, limit=None, order=None, context=None):
        Product = self.pool['product.product']

        # TODO filter on template only (howto in 7?)
        product_ids = Product.search(cr, uid, domain, offset=offset,
                limit=limit, order=order, context=context)
        records = Product.read(cr, uid, product_ids, fields, context=context)
        return records

    @_shop_logging
    def search_read_product_variant(self, cr, uid, shop, domain,
            fields=None, offset=0, limit=None, order=None, context=None):
        Product = self.pool['product.product']

        # TODO test returned data includes the data of the template of the variant
        product_ids = Product.search(cr, uid, domain, offset=offset,
                limit=limit, order=order, context=context)
        records = Product.read(cr, uid, product_ids, fields, context=context)
        return records

    @_shop_logging
    def get_inventory(self, cr, uid, shop, product_ids,
            context=None):
        Product = self.pool['product.product']

        fields = ['id', 'qty_available', 'virtual_available']
        records = Product.read(cr, uid, product_ids, fields, context=context)
        for record in records:
            for key in record.keys():
                if key not in fields:
                    record.pop(key)
        return records

    @_shop_logging
    def get_transfer_status(self, cr, uid, shop, domain,
            fields=None, offset=0, limit=None, order=None, context=None):
        Picking = self.pool['stock.picking.out']

        # TODO test with move_line
        domain.append(('sale_id', 'in', [so.id for so in shop.sale_order_ids]))
        picking_ids = Picking.search(cr, uid, domain, offset=offset,
                limit=limit, order=order, context=context)
        records = Picking.read(cr, uid, picking_ids, fields, context=context)
        return records

    @_shop_logging
    def get_payment_status(self, cr, uid, shop, domain, fields=None,
            offset=0, limit=None, order=None, context=None):
        Invoice = self.pool['account.invoice']

        #domain.append(('sale_order_id', 'in', [so.id for so in shop.sale_order_ids]))
        oids = Invoice.search(cr, uid, domain, offset=offset, limit=limit,
                order=order, context=context)
        records = Invoice.read(cr, uid, oids, fields, context=context)
        return records

    @_shop_logging
    def search_read_customer(self, cr, uid, shop, domain,
            fields=None, offset=0, limit=None, order=None, context=None):
        Partner = self.pool['res.partner']

        domain.append(('parent_id', '=', False))
        oids = Partner.search(cr, uid, domain, offset=offset, limit=limit,
                order=order, context=context)
        records = Partner.read(cr, uid, oids, fields, context=context)
        return records

    @_shop_logging
    def search_read_address(self, cr, uid, shop, domain,
            fields=None, offset=0, limit=None, order=None, context=None):
        Partner = self.pool['res.partner']

        domain.append(('parent_id', '!=', False))
        oids = Partner.search(cr, uid, domain, offset=offset, limit=limit,
                order=order, context=context)
        records = Partner.read(cr, uid, oids, fields, context=context)
        return records

    @_shop_logging
    def check_customer_credit(self, cr, uid, shop, customer_ids,
            context=None):
        Partner = self.pool['res.partner']

        domain = [('id', 'in', customer_ids),
                  ('customer_eshop_id', '=', shop.id)]
        oids = Partner.search(cr, uid, domain, context=context)
        fields = ['id', 'credit']
        records = Partner.read(cr, uid, oids, fields, context=context)
        for record in records:
            for key in record.keys():
                if key not in fields:
                    record.pop(key)
        return records

    @_shop_logging
    def get_docs(self, cr, uid, shop, sale_id, document_type,
            context=None):
        SaleOrder = self.pool['sale.order']

        model = document_type
        if document_type == 'sale.order':
            oid = sale_id
        elif document_type == 'account.invoice':
            invoice_ids = SaleOrder.read(cr, uid, sale_id, ['invoice_ids'],
                    context=context)['invoice_ids']
            oid = invoice_ids and invoice_ids[0] or False
        elif document_type == 'stock.picking':
            picking_ids = SaleOrder.read(cr, uid, sale_id, ['picking_ids'],
                    context=context)['picking_ids']
            oid = picking_ids and picking_ids[0] or False
            model = 'stock.picking.list.out'
        else:
            raise KeyError(document_type)
        return self._get_report(cr, uid, model, oid)

