from openerp.osv import orm, fields

STATES = [
    ('success', 'Success'),
    ('failure', 'Failure'),
]

class ecommerce_api_log(orm.Model):
    _name = 'ecommerce.api.log'
    _description = 'Ecommerce API Log'
    
    _columns = {
        'shop_id': fields.many2one('ecommerce.api.shop', 'Ecommerce API Shop', required=True),
        'state': fields.selection(STATES, 'State', default='success'),
        'method': fields.char('Method Name'),
        'args': fields.text('Method Arguments', help="Kept only on failure."),
        'exc_info': fields.text('Exception'),
        'create_date': fields.datetime('Create Date'),
        'create_uid': fields.many2one('res.users', 'User'),
    }

