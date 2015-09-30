import openerp
from openerp.osv import orm
from openerp.tools.translate import _

class ecommerce_api_v1(orm.AbstractModel):
    _name = 'ecommerce.api.v1'

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

        import pdb; pdb.set_trace()
        shops = self.pool['ecommerce.api.shop'].search(cr, uid, [('shop_identifier', '=', shop_identifier)], context=context)
        if not shops:
            raise openerp.exceptions.AccessError(_('No shop found with identifier %s') % shop_identifier)
        shop = self.pool['ecommerce.api.shop'].browse(cr, uid, shops[0], context=context)
        so_id = self.pool['sale.order'].create(cr, shop.internal_user_id.id, vals, context=context)
        return so_id

        #vals['warehouse_id'] = shop.default_warehouse_id.id
        #...
        #self.pool['sale.order'].onchange_(... vals )
        #...
        #return self.pool['sale.order'].create(cr, shop.internal_user_id.id, vals, context=context)

