# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import mock
from odoo.tests.common import TransactionCase
from ..hooks import post_init_hook_categorize_existing_products

MODULE_PATH = 'odoo.addons.website_sale_category_alphabetic'
MODEL_PATH = MODULE_PATH + '.models.product_template.ProductTemplate'


class TestProductTemplate(TransactionCase):

    @mock.patch(MODEL_PATH + '._add_alpha_website_categ', autospec=True)
    def test_post_init_hook_right_method_all_records(self, alpha_mock):
        """It should call correct method with set of all products as self"""
        test_registry = self.env.registry
        post_init_hook_categorize_existing_products(self.env.cr, test_registry)

        expected = self.env['product.template'].search([])
        alpha_mock.assert_called_once_with(expected)

    def test_post_init_hook_called_during_install(self):
        """It should be called during install, modifying prior products"""
        demo_record = self.env.ref('product.membership_1_product_template')
        exp = self.env.ref('website_sale_category_alphabetic.demo_category_s')

        self.assertIn(exp, demo_record.public_categ_ids)
