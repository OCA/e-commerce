from openerp import api, SUPERUSER_ID
from openerp.addons.sync_category_and_website_category.hooks \
    import copy_categories


def migrate(cr, version=None):
    """
    Previous version did not manage deleting of internal categories well
    this would leave lingering public categories. No more. we do a complete
    sync with this update to clean up possible remaining lingering public
    categories.Post init takes care of old installations this takes care of new
    ones.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    copy_categories(env)
