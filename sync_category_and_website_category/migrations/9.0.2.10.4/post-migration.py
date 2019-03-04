from openerp import api, SUPERUSER_ID
from openerp.addons.sync_category_and_website_category.sync_utils \
    import sync_translation


def migrate(cr, version=None):
    env = api.Environment(cr, SUPERUSER_ID, {})
    categories = env['product.category'].search([])
    for category in categories:
        try:
            sync_translation(env, category)
        except:
            continue
