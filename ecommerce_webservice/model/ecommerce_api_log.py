from openerp.osv import orm, fields

STATES = [
    ('success', 'Success'),
    ('failure', 'Failure'),
]


class ecommerce_api_log(orm.Model):
    _name = 'ecommerce.api.log'
    _description = 'Ecommerce API Log'
    _order = 'create_date DESC'

    _columns = {
        'shop_id': fields.many2one(
            'ecommerce.api.shop', 'Ecommerce API Shop',
            required=True, readonly=True, select=1),
        'state': fields.selection(
            STATES, 'State', default='success',
            readonly=True, select=1),
        'method': fields.char('Method Name', readonly=True, select=1),
        'args': fields.text(
            'Method Arguments', help="Kept only on failure.", readonly=True),
        'exc_info': fields.text('Exception', readonly=True),
        'create_date': fields.datetime('Create Date', readonly=True, select=1),
        'external_uid': fields.many2one(
            'res.users', 'User', readonly=True, select=1),
    }
