# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, SUPERUSER_ID


def copy_categories(env):
    # wipe all data of product.public.category
    env['product.public.category'].search([]).unlink()
    # copy all existing internal categories
    for private_category in env['product.category'].search(
            [], order='parent_left'):
        public_category = env['product.public.category'].create({
            'name': private_category.name.replace('_', ' '),
            'internal_category_id':  private_category.id,
            'sequence': private_category.sequence,
            'category_attributes': [(
                6, 0, private_category.product_field_ids.ids)],
        })
        # add products to new public_categories
        # Have to write no_sync, because normally changing directly the public
        # category is forbidden and popped out of the dict, this is a one way
        # sync module.
        # supporting multi internal categories from product_multi_category
        env['product.template'].with_context(no_sync=True).search([
            '|',
            ('categ_id', '=', private_category.id),
            ('categ_ids', '=', private_category.id)
        ]).write({
            'public_categ_ids': [(4, public_category.id)]
        })
    # add parents
    for private_category in env['product.category'].search([]):
        if private_category.parent_id:
            private_category.public_category_id.write(
                {'parent_id': private_category.parent_id.public_category_id.id}
            )
    return True


def post_init_hook(cursor, pool):
    # pylint: disable=W0613
    env = api.Environment(cursor, SUPERUSER_ID, {})
    copy_categories(env)
