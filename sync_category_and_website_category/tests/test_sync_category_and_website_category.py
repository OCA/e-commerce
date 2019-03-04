# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase
from ..hooks import post_init_hook


class TestSyncCategoryAndWebsiteCategory(TransactionCase):
    def setUp(self):  # pylint: disable=C0103
        super(TestSyncCategoryAndWebsiteCategory, self).setUp()

    def test_hooks(self):
        '''************** test hooks ****************'''
        post_init_hook(self.env.cr, self.env.registry)
        # check copied internal categories to external categories
        for private_category in self.env['product.category'].search([]):
            self.assertTrue(private_category.public_category_id)
            self.assertEqual(
                private_category.name.replace('_', ' '),
                private_category.public_category_id.name
            )

    def test_create_new_internal_cat(self):
        ''' check creating a new internal category'''
        parent_cat = self.env['product.category'].create({
            'name': 'base_category'
        })
        # create new internal category
        new_category = self.env['product.category'].create({
            'name': 'private_category',
            'parent_id': parent_cat.id,
        })
        self.assertEqual(
            new_category.id,
            new_category.public_category_id.internal_category_id.id
        )
        self.assertEqual(
            new_category.parent_id.id, parent_cat.id
        )

    def test_update_internal_category(self):
        ''' check updating a new internal category'''
        parent_cat = self.env['product.category'].create({
            'name': 'base_category'
        })
        updated_parent = self.env['product.category'].create({
            'name': 'minor_category'
        })
        # create new internal category
        new_category = self.env['product.category'].create({
            'name': 'private_category',
            'parent_id': parent_cat.id,
        })
        self.assertEqual(
            new_category.name,
            new_category.public_category_id.internal_category_id.name
        )
        self.assertEqual(
            new_category.parent_id.name, parent_cat.name)
        new_category.write({
            'name': 'new_name',
            'parent_id': updated_parent.id,
        })
        self.assertEqual(
            new_category.name,
            new_category.public_category_id.internal_category_id.name
        )
        self.assertEqual(
            new_category.parent_id.name,
            updated_parent.name
        )
        self.assertEqual(
            new_category.parent_id.id, updated_parent.id)
