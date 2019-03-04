from openerp import api, SUPERUSER_ID


def migrate(cr, version=None):
    env = api.Environment(cr, SUPERUSER_ID, {})
    """
    It is a lot easier to remove  the few non published categories than
    ADD all the categories that should be on website.
    The first installed version had default=False. this mig script fixes that.
    """
    env['product.category'].search([]).write({'published': True})
