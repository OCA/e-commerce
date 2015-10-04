import uuid

from openerp.osv import orm, fields
from openerp.tools.translate import _

class ecommerce_api_shop(orm.Model):
    _name = 'ecommerce.api.shop'
    _rec_name = 'shop_identifier'
    _description = 'Ecommerce API Shop'

    _columns = {
        # TODO: rename 'shop_identifier' to something less ambiguous like 'name'
        'shop_identifier': fields.char('Shop Identifier', size=8, required=True),
        'external_user_id': fields.many2one('res.users', 'Service Public User', required=True),
        'internal_user_id': fields.many2one('res.users', 'Service Internal User', required=True),
        'enable_logs': fields.boolean('Enable Logs',
            help="Activate the detailed logging in database of all the incoming calls."),
        'logs_all_on_success': fields.boolean('Log all on success',
            help="Logs method arguments on success as well."),
        'default_shop_id': fields.many2one('sale.shop', 'Default Sale Shop', required=True,
            help="Shop which will be set on the sales orders."),
        #'default_warehouse_id': fields.many2one('stock.warehouse', 'Default Warehouse', required=True,
        #    help="The warehouse on which the sales orders will be created and the stock of the products be computed. Default to company's warehouse."),

        'partner_ids': fields.one2many('res.partner', 'eshop_id', 'Customers'),
        #'partner_address_ids': fields.one2many('res.partner', 'eshop_id', 'Addresses'),
        #'sale_order_ids': fields.one2many('sale.order', 'eshop_id', 'Sales Orders'),
    }

    _sql_constraints = [
        ('unique_shop_identifier', 'unique(shop_identifier)', _('There is already an eshop with this identifier. Chose another shop identifier.')),
    ]

    def default_get(self, cr, uid, fields_list, context=None):
        data = super(ecommerce_api_shop, self).default_get(cr, uid, fields_list, context)
        shop_identifier = str(uuid.uuid4())[:8]
        internal_user_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'ecommerce_webservice', 'ecommerce_api_internal_user')[1]
        default_shop_id = self.pool['sale.order']._get_default_shop(cr, uid, context)
        data.update({
            'shop_identifier': shop_identifier,
            'internal_user_id': internal_user_id,
            'default_shop_id': default_shop_id,
            })
        return data

