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

from domain_helper import issearchdomain, searchargs

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
                    Log = self.pool['ecommerce.api.log']
                    Log.create(new_cr, internal_uid, values, context)
                    new_cr.commit()
                    new_cr.close()
        return wrapped

    def _find_shop(self, cr, uid, shop_identifier, context=None):
        Shop = self.pool['ecommerce.api.shop']
        shops = Shop.search(cr, uid,
                [('shop_identifier', '=', shop_identifier)], context=context)
        if not shops:
            raise openerp.exceptions.AccessError(
                    _('No shop found with identifier %s') % shop_identifier)
        shop = Shop.browse(cr, uid, shops[0], context=context)
        return shop

    def _update_vals_for_country_id(self, cr, uid, vals, context=None):
        if 'country' in vals:
            country_ids = self.pool['res.country'].name_search(cr, uid,
                    vals['country'], context=context)
            country_id = country_ids[0][0] if country_ids else False
            vals.pop('country')
            vals['country_id'] = country_id

    def _search_read_anything(self, cr, uid, model, domain, fields=None,
            offset=0, limit=None, order=None, context=None):
        if issearchdomain(domain):
            searchargs((domain,))
        oids = self.pool[model].search(cr, uid, domain, offset=offset,
                limit=limit, order=order, context=context)
        records = self._read_with_cast(cr, uid, model, oids, fields, context=context)
        return records

    def _read_with_cast(self, cr, uid, model, oids, fields=None, context=None):
        Model = self.pool[model]
        records = Model.read(cr, uid, oids, fields, context=context)

        if records:
            fields_to_cast = []
            all_fields = fields or Model._all_columns.keys()
            for field_name in all_fields:
                field = Model._all_columns.get(field_name)
                if field and field.column._type == 'many2one':
                    fields_to_cast.append(field_name)

            if fields_to_cast:
                for i, record in enumerate(records):
                    for field_name in fields_to_cast:
                        column = Model._all_columns[field_name].column
                        if column._type == 'many2one':
                            if record[field_name]:
                                # (1, 'foo') -> {'id': 1, 'name': 'foo'}
                                record[field_name] = dict(
                                        zip(('id', 'name'), record[field_name]))
        if fields:
            for record in records:
                for key in record.keys():
                    if key not in fields:
                        del record[key]
        return records

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

    def _prepare_sale_order(self, cr, uid, shop, vals, context=None):
        SO = self.pool['sale.order']

        vals.update({
            'state': 'draft',
            'shop_id': shop.default_shop_id.id,
            'eshop_id': shop.id,
            })

        onchange_vals = {}
        if 'partner_id' in vals:
            ocv = SO.onchange_partner_id(cr, uid, None, vals['partner_id'],
                    context=context)
            onchange_vals.update(ocv['value'])
        if 'shop_id' in vals:
            ocv = SO.onchange_shop_id(cr, uid, None, vals['shop_id'],
                    context=context)
            onchange_vals.update(ocv['value'])

        # fields in vals prevail over fields returned by onchange
        for key in onchange_vals.keys():
            if key in vals:
                onchange_vals.pop(key)
        vals.update(onchange_vals)

    def _prepare_sale_order_lines(self, cr, uid, shop, vals, context=None):
        SOL = self.pool['sale.order.line']

        raw_order_line = vals.pop('order_line', [])
        order_line = []
        for line in raw_order_line:
            onchange_vals = {}
            if 'product_id' in line:
                ocv = SOL.product_id_change(cr, uid, None,
                       vals.get('pricelist_id'), line['product_id'],
                       line.get('product_uom_qty'), line.get('product_uom'),
                       line.get('product_uos_qty'), line.get('product_uos'),
                       line.get('name'), vals['partner_id'],
                       date_order=vals.get('date_order'), context=context)
                onchange_vals.update(ocv['value'])
            for key in onchange_vals.keys():
                if key in line:
                    onchange_vals.pop(key)
            line.update(onchange_vals)
            order_line.append([0, False, line])

        if order_line:
            vals['order_line'] = order_line

    @_shop_logging
    def create_sale_order(self, cr, uid, shop, vals, context=None):
        self._prepare_sale_order(cr, uid, shop, vals, context)
        self._prepare_sale_order_lines(cr, uid, shop, vals, context)
        so_id = self.pool['sale.order'].create(cr, uid, vals, context=context)
        return so_id

    @_shop_logging
    def search_read_product_template(self, cr, uid, shop, domain,
            fields=None, offset=0, limit=None, order=None, context=None):
        model = 'product.product'
        domain.append(('variants', '=', False))
        return self._search_read_anything(cr, uid, model, domain,
                fields, offset, limit, order, context)

    @_shop_logging
    def search_read_product_variant(self, cr, uid, shop, domain,
            fields=None, offset=0, limit=None, order=None, context=None):
        model = 'product.product'
        return self._search_read_anything(cr, uid, model, domain,
                fields, offset, limit, order, context)

    @_shop_logging
    def get_inventory(self, cr, uid, shop, product_ids,
            context=None):
        fields = ['id', 'qty_available', 'virtual_available']
        records = self._read_with_cast(cr, uid, 'product.product',
                product_ids, fields, context=context)
        return records

    @_shop_logging
    def get_transfer_status(self, cr, uid, shop, domain,
            fields=None, offset=0, limit=None, order=None, context=None):
        model = 'stock.picking.out'
        domain.append(('sale_id', 'in', [so.id for so in shop.sale_order_ids]))
        return self._search_read_anything(cr, uid, model, domain,
                fields, offset, limit, order, context)

    @_shop_logging
    def get_payment_status(self, cr, uid, shop, domain, fields=None,
            offset=0, limit=None, order=None, context=None):
        model = 'account.invoice'
        # take ony invoice generated by SO of shop
        domain.append(('sale_order_ids', 'in', [so.id for so in shop.sale_order_ids]))
        return self._search_read_anything(cr, uid, model, domain,
                fields, offset, limit, order, context)

    @_shop_logging
    def search_read_customer(self, cr, uid, shop, domain,
            fields=None, offset=0, limit=None, order=None, context=None):
        model = 'res.partner'
        domain.append(('parent_id', '=', False))
        return self._search_read_anything(cr, uid, model, domain,
                fields, offset, limit, order, context)

    @_shop_logging
    def search_read_address(self, cr, uid, shop, domain,
            fields=None, offset=0, limit=None, order=None, context=None):
        model = 'res.partner'
        domain.append(('parent_id', '!=', False))
        return self._search_read_anything(cr, uid, model, domain,
                fields, offset, limit, order, context)

    @_shop_logging
    def check_customer_credit(self, cr, uid, shop, customer_ids,
            context=None):
        domain = [('id', 'in', customer_ids),
                  ('customer_eshop_id', '=', shop.id)]
        oids = self.pool['res.partner'].search(cr, uid, domain, context=context)
        fields = ['id', 'credit']
        records = self._read_with_cast(cr, uid, 'res.partner', oids, fields,
                context=context)
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
            message = 'Printing %s is not supported. Is the spelling correct?'
            raise openerp.exceptions.AccessError(_(message) % document_type)
        return self._get_report(cr, uid, model, oid)

