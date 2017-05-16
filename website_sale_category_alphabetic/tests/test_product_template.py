# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import mock
from odoo.tests.common import TransactionCase

MODULE_PATH = 'odoo.addons.website_sale_category_alphabetic'
MODEL_PATH = MODULE_PATH + '.models.product_template.ProductTemplate'


class TestProductTemplate(TransactionCase):

    @mock.patch(MODEL_PATH + '._add_alpha_website_categ', autospec=True)
    def test_create_calls_correct_method_on_new_record(self, alpha_mock):
        """It should call correct method with new record as self"""
        demo_record = self.env.ref('website_sale_category_alphabetic.demo_1')
        test_record = demo_record.copy()

        alpha_mock.assert_called_once_with(test_record)

    def test_add_alpha_website_categ_alpha_product_existing(self):
        """It should add correct existing category to alpha products"""
        test_record = self.env.ref('website_sale_category_alphabetic.demo_1')
        test_record.public_categ_ids = None
        test_record._add_alpha_website_categ()

        exp = self.env.ref('website_sale_category_alphabetic.demo_category_a')
        self.assertEqual(test_record.public_categ_ids, exp)

    def test_add_alpha_website_categ_numerical_product_existing(self):
        """It should add correct existing category to numerical products"""
        test_record = self.env.ref('website_sale_category_alphabetic.demo_3')
        test_record.public_categ_ids = None
        test_record._add_alpha_website_categ()

        exp = self.env.ref('website_sale_category_alphabetic.demo_category_#')
        self.assertEqual(test_record.public_categ_ids, exp)

    def test_add_alpha_website_categ_other_product_existing(self):
        """It should add correct existing category to other products"""
        test_record = self.env.ref('website_sale_category_alphabetic.demo_4')
        test_record.public_categ_ids = None
        test_record._add_alpha_website_categ()

        exp = self.env.ref('website_sale_category_alphabetic.demo_category_*')
        self.assertEqual(test_record.public_categ_ids, exp)

    def test_add_alpha_website_categ_alpha_product_new(self):
        """It should add correct new category to alpha products if no match"""
        test_record = self.env.ref('website_sale_category_alphabetic.demo_1')
        test_record.public_categ_ids.unlink()
        test_record._add_alpha_website_categ()

        expect_parent = self.env.ref('website_sale_category_alphabetic.base')
        self.assertEqual(test_record.public_categ_ids.name, 'A')
        self.assertEqual(test_record.public_categ_ids.sequence, ord('A'))
        self.assertEqual(test_record.public_categ_ids.parent_id, expect_parent)

    def test_add_alpha_website_categ_numerical_product_new(self):
        """It should add correct new category to number products if no match"""
        test_record = self.env.ref('website_sale_category_alphabetic.demo_3')
        test_record.public_categ_ids.unlink()
        test_record._add_alpha_website_categ()

        expect_parent = self.env.ref('website_sale_category_alphabetic.base')
        self.assertEqual(test_record.public_categ_ids.name, '#')
        self.assertEqual(test_record.public_categ_ids.sequence, 0x10ffff + 1)
        self.assertEqual(test_record.public_categ_ids.parent_id, expect_parent)

    def test_add_alpha_website_categ_other_product_new(self):
        """It should add correct new category to other products if no match"""
        test_record = self.env.ref('website_sale_category_alphabetic.demo_4')
        test_record.public_categ_ids.unlink()
        test_record._add_alpha_website_categ()

        expect_parent = self.env.ref('website_sale_category_alphabetic.base')
        self.assertEqual(test_record.public_categ_ids.name, '*')
        self.assertEqual(test_record.public_categ_ids.sequence, 0x10ffff + 2)
        self.assertEqual(test_record.public_categ_ids.parent_id, expect_parent)

    def test_add_alpha_website_categ_keep_prior_categs(self):
        """It should not remove any categories already mapped to record"""
        test_record = self.env.ref('website_sale_category_alphabetic.demo_1')
        test_category = test_record.public_categ_ids
        test_record.name = 's' + test_record.name
        test_record._add_alpha_website_categ()

        self.assertIn(test_category, test_record.public_categ_ids)
