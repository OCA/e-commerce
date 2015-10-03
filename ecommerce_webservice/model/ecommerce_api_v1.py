import sys
import traceback
from functools import wraps

import sql_db
import openerp
from openerp import SUPERUSER_ID
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
                }
                result = method(self, cr, uid, shop_identifier, *args, **kwargs)
            except:
                exc_info = sys.exc_info()
                values.update({
                    'args': str(args), # TODO test unicode (maybe just pass args)
                    'state': 'failure',
                    'exc_info': traceback.format_exc(exc_info),
                    })
                new_cr = sql_db.db_connect(cr.dbname).cursor()
                self.pool['ecommerce.api.log'].create(new_cr, SUPERUSER_ID, values, context)
                new_cr.commit()
                raise exc_info[0], exc_info[1], exc_info[2]
            else:
                values.update({
                    'state': 'success',
                    })
                new_cr = sql_db.db_connect(cr.dbname).cursor()
                self.pool['ecommerce.api.log'].create(new_cr, SUPERUSER_ID, values, context)
                new_cr.commit()
                return result
        return wrapped

    def _find_shop(self, cr, uid, shop_identifier, context=None):
        shops = self.pool['ecommerce.api.shop'].search(cr, uid, [('shop_identifier', '=', shop_identifier)], context=context)
        if not shops:
            raise openerp.exceptions.AccessError(_('No shop found with identifier %s') % shop_identifier)
        shop = self.pool['ecommerce.api.shop'].browse(cr, uid, shops[0], context=context)
        return shop


    @_shop_logging
    def create_customer(self, cr, uid, shop_identifier, vals, context=None):
        """
        vals:
        parent_id integer (id) ID of the partner
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

        if 'country' in vals:
            country_ids = self.pool['res.country'].name_search(cr, uid, vals['country'], context=context)
            country_id = country_ids[0][0] if country_ids else False
        vals.update({
            'customer': True,
            'country_id': country_id,
            'eshop_id': shop.id, # link to shop.partner_ids
            })
        customer_id = self.pool['res.partner'].create(cr, uid, vals, context)
        return customer_id

    def create_sale_order(self, cr, uid, shop_identifier, vals, context=None):
        """
        Create a 'sale.order' and returns its ID.

        vals:
        name                string            Order Reference
        client_order_ref    string            Customer Reference
        date_order          date (YYYY-mm-dd) Date of the order
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

        shops = self.pool['ecommerce.api.shop'].search(cr, uid, [('shop_identifier', '=', shop_identifier)], context=context)
        if not shops:
            raise openerp.exceptions.AccessError(_('No shop found with identifier %s') % shop_identifier)
        shop = self.pool['ecommerce.api.shop'].browse(cr, uid, shops[0], context=context)
        so_id = self.pool['sale.order'].create(cr, shop.internal_user_id.id, vals, context=context)
        # add so_id to shop.sale_order_ids
        return so_id

        #vals['warehouse_id'] = shop.default_warehouse_id.id
        #...
        #self.pool['sale.order'].onchange_(... vals )
        #...
        #return self.pool['sale.order'].create(cr, shop.internal_user_id.id, vals, context=context)

