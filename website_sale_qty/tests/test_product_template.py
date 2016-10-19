# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import date, timedelta
from openerp.tests.common import TransactionCase


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

        self.test_pricelist_1 = self.env['product.pricelist'].create({
            'currency_id': self.env.ref('base.USD').id,
            'name': 'Test Pricelist 1',
        })
        self.test_pricelist_2 = self.env['product.pricelist'].create({
            'currency_id': self.env.ref('base.USD').id,
            'name': 'Test Pricelist 2',
        })
        self.pricelists = self.env['product.pricelist'].search([
            ('id', '>', 0),
        ])

        self.env['product.pricelist.item'].search([('id', '>', 0)]).unlink()

    def test_price_quantity_tiers_no_matches(self):
        '''The tiers for each pricelist should be empty if no prices match'''
        for pricelist_id in self.pricelists.ids:
            self.assertEqual(
                self.test_template.price_quantity_tiers[pricelist_id],
                [],
                msg='Pricelist %s should not have tiers' % pricelist_id,
            )

    def test_price_quantity_tiers_no_template_matches(self):
        '''The tiers should be empty if no prices match at template level'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist_1.id,
            'applied_on': '3_global',
            'compute_price': 'fixed',
            'fixed_price': 1,
        })
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist_1.id,
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
            'pricelist_id': self.test_pricelist_2.id,
            'applied_on': '0_product_variant',
            'compute_price': 'fixed',
            'fixed_price': 1,
            'product_id': test_product.id,
        })

        for pricelist_id in self.pricelists.ids:
            self.assertEqual(
                self.test_template.price_quantity_tiers[pricelist_id],
                [],
                msg='Pricelist %s should not have tiers' % pricelist_id,
            )

    def test_price_quantity_tiers_match_wrong_start_date(self):
        '''The tiers should be empty if no price matches have started yet'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist_1.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 1,
            'product_tmpl_id': self.test_template.id,
            'date_start': date.today() + timedelta(days=1),
        })

        for pricelist_id in self.pricelists.ids:
            self.assertEqual(
                self.test_template.price_quantity_tiers[pricelist_id],
                [],
                msg='Pricelist %s should not have tiers' % pricelist_id,
            )

    def test_price_quantity_tiers_match_wrong_end_date(self):
        '''The tiers should be empty if all price matches have ended already'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist_1.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 1,
            'product_tmpl_id': self.test_template.id,
            'date_end': date.today() - timedelta(days=1),
        })

        for pricelist_id in self.pricelists.ids:
            self.assertEqual(
                self.test_template.price_quantity_tiers[pricelist_id],
                [],
                msg='Pricelist %s should not have tiers' % pricelist_id,
            )

    def test_price_quantity_tiers_valid_matches(self):
        '''Tiers should reflect all matches, plus min qty 1, ordered by qty'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist_1.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 1,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': 2,
        })
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist_1.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 0.8,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': 20,
        })
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist_2.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 0.7,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': 3,
        })

        self.assertEqual(
            self.test_template.price_quantity_tiers[self.test_pricelist_1.id],
            [(1, 1), (2, 1), (20, 0.8)],
        )
        self.assertEqual(
            self.test_template.price_quantity_tiers[self.test_pricelist_2.id],
            [(1, 1), (3, 0.7)],
        )

    def test_price_quantity_tiers_invalid_min_quantities(self):
        '''The tiers should treat min quantities below 1 as if they were 1'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist_1.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 0.8,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': -3,
        })
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist_1.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 0.7,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': 3,
        })

        self.assertEqual(
            self.test_template.price_quantity_tiers[self.test_pricelist_1.id],
            [(1, 0.8), (3, 0.7)],
        )

    def test_price_quantity_tiers_qty_1_alone(self):
        '''A single price tier with a min quantity of 1 should be rejected'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist_1.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 1,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': 1,
        })

        self.assertEqual(
            self.test_template.price_quantity_tiers[self.test_pricelist_1.id],
            [],
        )

    def test_price_quantity_tiers_first_variant_price_rule(self):
        '''The tiers don't show match if 1st variant has same qty price rule'''
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist_1.id,
            'applied_on': '1_product',
            'compute_price': 'fixed',
            'fixed_price': 1,
            'product_tmpl_id': self.test_template.id,
            'min_quantity': 2,
        })
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.test_pricelist_1.id,
            'applied_on': '0_product_variant',
            'compute_price': 'fixed',
            'fixed_price': 1.5,
            'product_id': self.test_template.product_variant_ids[0].id,
            'min_quantity': 2,
        })

        self.assertEqual(
            self.test_template.price_quantity_tiers[self.test_pricelist_1.id],
            [],
        )
