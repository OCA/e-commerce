from openerp import api, SUPERUSER_ID
from openerp.addons.sync_category_and_website_category.hooks \
    import copy_categories


def migrate(cr, version=None):
    """
    we had a version that did not trigger the sync correctly, again.
    the only way to fix the db is to launch this. could remove in future
    if becomes a public module
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['product.template'].search([]).write({'website_size_x': 2})
    env['product.template'].search([]).write({'website_size_x': 1})
    copy_categories(env)
