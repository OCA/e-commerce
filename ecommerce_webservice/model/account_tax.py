from openerp.osv import orm, fields
from openerp.tools.translate import _

class Tax(orm.Model):
    _inherit = 'account.tax'

    _columns = {
        'api_code': fields.char('API Code'),
    }

    _sql_constraints = [
        ('api_code_uniq', 'unique(api_code, company_id)',
            _('This API Code already exists in this company.')),
    ]

