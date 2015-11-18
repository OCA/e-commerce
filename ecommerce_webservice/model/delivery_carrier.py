from openerp.osv import orm, fields
from openerp.tools.translate import _


class DeliveryCarrier(orm.Model):
    _inherit = 'delivery.carrier'

    _columns = {
        'api_code': fields.char('API Code'),
    }

    _sql_constraints = [
        ('api_code_uniq', 'unique(api_code)',
            _('This API Code already exists.')),
    ]
