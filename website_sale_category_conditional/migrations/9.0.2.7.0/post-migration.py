from openerp import api, SUPERUSER_ID


def migrate(cr, version=None):
    env = api.Environment(cr, SUPERUSER_ID, {})
    """
    Customer wants to start with all unpublished
    """
    env['product.category'].search([]).write({'published': False})
