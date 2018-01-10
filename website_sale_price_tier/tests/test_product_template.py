# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import date, timedelta
from mock import patch
from odoo.tests.common import TransactionCase

WEBSITE_PATH = 'odoo.addons.website.models.website.Website.get_current_website'
SALE_ORDER_PATH = 'odoo.addons.website_sale.models.sale_order'
PRICELIST_PATH = SALE_ORDER_PATH + '.Website.get_current_pricelist'


class TestProductTemplate(TransactionCase):

    def setUp(self):
        super(TestProductTemplate, self).setUp()

        self.test_template = self.env['product.template'].create({
            'categ_id': self.env.ref('product.product_category_1').id,
            'name': 'Test Template',
            'type': 'consu',
            'uom_id': self.env.ref('product.product_uom_unit').id,
            'uom_po_id': self.env.ref('product.product_uom_unit').id,
        })

        self.test_website = self.env.ref('website.default_website')
        self.test_website.show_implicit_price_tier = True
        website_patcher = patch(WEBSITE_PATH)
        self.addCleanup(website_patcher.stop)
        website_patcher.start().return_value = self.test_website

        self.test_pricelist = self.env['product.pricelist'].create({
            'currency_id': self.env.ref('base.USD').id,
            'name': 'Test Pricelist 1',
        })
        pricelist_patcher = patch(PRICELIST_PATH)
        self.addCleanup(pricelist_patcher.stop)
        pricelist_patcher.start().return_value = self.test_pricelist

        self.env['product.pricelist.item'].search([('id', '>', 0)]).unlink()

    def test_price_quantity_tiers_no_matches(self):
        '''The tiers should be empty if no prices match'''
        self.assertEqual(self.test_template.price_quantity_tiers, [])

    def test_price_quantity_tiers_no_template_matches(self):
        '''The tiers should be empty if no prices match at template level'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist.id,
            'applied_on': '3_global',
            'compute_price': 'fixed',
            'fixed_price': 1,
        })
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist.id,
            'applied_on': '2_product_category',
            'compute_price': 'fixed',
            'fixed_price': 1,
            'categ_id': self.test_template.categ_id.id,
        })
        test_product = self.env['product.product'].create({
            'categ_id': self.test_template.categ_id.id,
            'name': 'Test Product',
            'product_tmpl_id': self.test_template.id,

        })
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist.id,
            'applied_on': '0_product_variant',
            'compute_price': 'fixed',
            'fixed_price': 1,
            'product_id': test_product.id,
        })

        self.assertEqual(self.test_template.price_quantity_tiers, [])

    def test_price_quantity_tiers_match_wrong_start_date(self):
        '''The tiers should be empty if no price matches have started yet'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 1,
            'product_tmpl_id': self.test_template.id,
            'date_start': date.today() + timedelta(days=1),
        })

        self.assertEqual(self.test_template.price_quantity_tiers, [])

    def test_price_quantity_tiers_match_wrong_end_date(self):
        '''The tiers should be empty if all price matches have ended already'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 1,
            'product_tmpl_id': self.test_template.id,
            'date_end': date.today() - timedelta(days=1),
        })

        self.assertEqual(self.test_template.price_quantity_tiers, [])

    def test_price_quantity_tiers_valid_matches(self):
        '''Tiers should reflect all matches, plus min qty 1, ordered by qty'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 1,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': 2,
        })
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 0.73,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': 20,
        })

        self.assertEqual(
            self.test_template.price_quantity_tiers,
            [[1, 1.0], [2, 2.0], [20, 14.6]],
        )

    def test_price_quantity_tiers_invalid_min_quantities(self):
        '''The tiers should treat min quantities below 1 as if they were 1'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 0.8,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': -3,
        })
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 0.7,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': 3,
        })

        self.assertEqual(
            self.test_template.price_quantity_tiers,
            [[1, 0.8], [3, 2.1]],
        )

    def test_price_quantity_tiers_qty_1_alone(self):
        '''A single price tier with a min quantity of 1 should be rejected'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 1,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': 1,
        })

        self.assertEqual(self.test_template.price_quantity_tiers, [])

    def test_price_quantity_tiers_first_variant_price_rule(self):
        '''Tiers show variant pricing if 1st variant has same qty price rule'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 1,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': 2,
        })
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist.id,
            'applied_on': '0_product_variant',
            'compute_price': 'fixed',
            'fixed_price': 1.5,
            'product_id': self.test_template.product_variant_ids[0].id,
            'min_quantity': 2,
        })

        self.assertEqual(
            self.test_template.price_quantity_tiers,
            [[1, 1.0], [2, 3.0]],
        )

    def test_price_quantity_tiers_taxes_included(self):
        '''It should correctly include taxes in tier subtotals'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 1,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': 2,
        })
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 0.73,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': 20,
        })
        self.env.ref('sale.group_show_price_subtotal').unlink()
        test_tax = self.env.ref('website_sale_price_tier.account_tax_1_demo')
        self.test_template.taxes_id = test_tax

        self.assertEqual(
            self.test_template.price_quantity_tiers,
            [[1, 1.1], [2, 2.2], [20, 16.06]],
        )

    def test_price_quantity_tiers_correct_rounding(self):
        '''It should round prices before computing subtotal (i.e. like cart)'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 0.73475,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': 20,
        })

        self.assertEqual(
            self.test_template.price_quantity_tiers,
            [[1, 1.0], [20, 14.60]],
        )

    def test_price_quantity_tiers_conditional_implicit_tier(self):
        '''It should not add implicit qty 1 tier if this setting is off'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 0.5,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': 20,
        })
        self.test_website.show_implicit_price_tier = False

        self.assertEqual(
            self.test_template.price_quantity_tiers,
            [[20, 10.0]],
        )
