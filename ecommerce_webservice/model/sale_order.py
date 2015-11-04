from openerp.osv import orm, fields


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'eshop_id': fields.many2one(
            'ecommerce.api.shop',
            'Ecommerce API Shop'),
    }
