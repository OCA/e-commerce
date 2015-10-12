import sys
import time
import traceback
from functools import wraps

import sql_db
import openerp
from openerp.osv import orm
from openerp.tools.translate import _

class ecommerce_api_v1(orm.AbstractModel):
    _name = 'ecommerce.api.v1'

    def _shop_logging(method):
        @wraps(method)
        def wrapped(self, cr, uid, shop_identifier, *args, **kwargs):
            context = None
            if context in kwargs:
                context = kwargs['context']
            shop = self._find_shop(cr, uid, shop_identifier, context)
            try:
                values = {
                    'shop_id': shop.id,
                    'method': method.func_name,
                    # serialize args before calling as they might get modified
                    'args': "args:\n%s\n\nkwargs:\n%s" % (args, kwargs),
                    }
                result = method(self, cr, uid, shop_identifier, *args, **kwargs)
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
                    self.pool['ecommerce.api.log'].create(new_cr, uid, values, context)
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


    @_shop_logging
    def create_customer(self, cr, uid, shop_identifier, vals, context=None):
        """
        vals:
        name      string       Name
        active    boolean      Active?
        street    string       Street
        street2   string       Street2
        city      string       City
        zip       string       ZIP
        country   string       Country Code
        phone     string       Phone
        mobile    string       Mobile
        fax       string       Fax
        email     string       email
        """

        shop = self._find_shop(cr, uid, shop_identifier, context)
        iuid = shop.internal_user_id.id

        self._update_vals_for_country_id(cr, iuid, vals, context)
        vals.update({
            'customer': True,
            'type': 'default',
            'customer_eshop_id': shop.id, # link to shop.partner_ids
            })
        customer_id = self.pool['res.partner'].create(cr, iuid, vals, context)
        return customer_id

    @_shop_logging
    def update_customer(self, cr, uid, shop_identifier, partner_id, vals, context=None):
        """
        vals:
        name      string       Name
        active    boolean      Active?
        street    string       Street
        street2   string       Street2
        city      string       City
        zip       string       ZIP
        country   string       Country Code
        phone     string       Phone
        mobile    string       Mobile
        fax       string       Fax
        email     string       email
        """

        shop = self._find_shop(cr, uid, shop_identifier, context)
        iuid = shop.internal_user_id.id

        self._update_vals_for_country_id(cr, uid, vals, context)
        return self.pool['res.partner'].write(cr, iuid, partner_id, vals, context=context)

    @_shop_logging
    def create_customer_address(self, cr, uid, shop_identifier, customer_id, vals, context=None):
        """
        vals:
        name      string       Name
        active    boolean      Active?
        street    string       Street
        street2   string       Street2
        city      string       City
        zip       string       ZIP
        country   string       Country Code
        type      selection    'default', 'invoice', 'delivery', 'contact' or 'other'
        phone     string       Phone
        mobile    string       Mobile
        fax       string       Fax
        email     string       email
        """

        shop = self._find_shop(cr, uid, shop_identifier, context)
        iuid = shop.internal_user_id.id

        self._update_vals_for_country_id(cr, iuid, vals, context)
        vals.update({
            'customer': True,
            'parent_id': customer_id,
            'address_eshop_id': shop.id, # link to shop.partner_ids
            })
        address_id = self.pool['res.partner'].create(cr, iuid, vals, context)
        return address_id

    @_shop_logging
    def update_customer_address(self, cr, uid, shop_identifier, address_ids, vals, context=None):
        """
        vals:
        name      string       Name
        active    boolean      Active?
        street    string       Street
        street2   string       Street2
        city      string       City
        zip       string       ZIP
        country   string       Country Code
        type      selection    'default', 'invoice', 'delivery', 'contact' or 'other'
        phone     string       Phone
        mobile    string       Mobile
        fax       string       Fax
        email     string       email
        """

        shop = self._find_shop(cr, uid, shop_identifier, context)
        iuid = shop.internal_user_id.id

        self._update_vals_for_country_id(cr, uid, vals, context)
        return self.pool['res.partner'].write(cr, iuid, address_ids, vals, context=context)

    @_shop_logging
    def create_sale_order(self, cr, uid, shop_identifier, vals, context=None):
        """
        Create a 'sale.order' and returns its ID.

        vals:
        name                string            Order Reference
        client_order_ref    string            Customer Reference
        date_order          string YYYY-mm-dd Date of the order
        note                text              Terms and conditions
        origin              string            Source document
        partner_id          integer (id)      Odoo ID of the customer
        partner_invoice_id  integer (id)      Odoo ID of the invoice address
        partner_shipping_id integer (id)      Odoo ID of the shipping address
        order_line          list              List of lines (see line details below)

        order_line:
        product_id      integer (id) ID of the product
        name            string       Description of the product, if empty, use the Odoo one
        price_unit      float        Unit price
        discount        float        Discount (%)
        product_uom_qty float        Quantity
        sequence        integer      Sequence of the line (asc order, 0 is the first)
        """

        shop = self._find_shop(cr, uid, shop_identifier, context)
        iuid = shop.internal_user_id.id
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
            ocv = SO.onchange_partner_id(cr, iuid, None, vals['partner_id'], context=context)
            onchange_vals.update(ocv['value'])
        if 'shop_id' in vals:
            ocv = SO.onchange_shop_id(cr, iuid, None, vals['shop_id'], context=context)
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
                ocv = SOL.product_id_change(cr, iuid, None,
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
        so_id = SO.create(cr, iuid, vals, context=context)
        return so_id

