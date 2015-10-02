from openerp.osv import orm, fields

class Partner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'eshop_id': fields.many2one('ecommerce.api.shop', 'Ecommerce API Shop'),
    }

