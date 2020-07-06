# Copyright 2020 Commown SCIC SAS (https://commown.fr)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import OrderedDict

from odoo.addons.website_sale_affiliate_product_restriction.tests import (
    test_sale_affiliate)


class TestWebsiteSaleAffiliatePortal(test_sale_affiliate.
                                     TestWebsiteSaleAffiliateProductRestriction):

    @classmethod
    def setUpClass(cls):
        super(TestWebsiteSaleAffiliatePortal, cls).setUpClass()
        cls.pp1 = cls.env.ref('product.product_product_1')  # Virtual Interior Design
        cls.pp2 = cls.env.ref('product.product_product_2')  # Virtual Home Staging
        cls.pp3 = cls.env.ref('product.product_product_3')  # Desk Combination

    def create_sales(self):
        sess = self.fake_session
        sess['affiliate_request'] = self.create_affiliate_req('2018-01-05').id
        self.create_sale([(self.pp1, 1)], 'draft', create_date='2018-01-05')

        sess['affiliate_request'] = self.create_affiliate_req('2018-01-13').id
        self.create_sale([(self.pp1, 3), (self.pp2, 2)], create_date='2018-01-13')

        sess['affiliate_request'] = self.create_affiliate_req('2018-02-20').id
        self.create_sale([(self.pp2, 3), (self.pp3, 3)], create_date='2018-02-20')
        self.create_sale([(self.pp2, 4)], create_date='2018-02-21')

        sess['affiliate_request'] = self.create_affiliate_req('2018-03-20').id
        self.create_sale(
            [(self.pp2, 2), (self.pp1, 1)], 'draft', create_date='2018-03-20')
        self.create_sale([(self.pp3, 8), (self.pp2, 1)], create_date='2018-03-20')

        sess['affiliate_request'] = self.create_affiliate_req('2018-04-20').id
        self.create_sale([(self.pp3, 4), (self.pp1, 7)], create_date='2018-04-20')

        sess['affiliate_request'] = self.create_affiliate_req('2018-05-03').id

    def test_report_no_product_restriction(self):
        self.affiliate.gain_type = 'fixed'
        self.affiliate.gain_value = 1

        self.create_sales()

        self.assertEqual(OrderedDict([
            ('2018-01', OrderedDict([
                ('by-product', OrderedDict([
                    (u'Virtual Home Staging', {'validated': 2, 'gain': 2.0}),
                    (u'Virtual Interior Design', {'validated': 3, 'gain': 3.0}),
                ])),
                ('visits', 2)])),
            ('2018-02', OrderedDict([
                ('by-product', OrderedDict([
                    (u'Desk Combination', {'validated': 3, 'gain': 3.0}),
                    (u'Virtual Home Staging', {'validated': 7, 'gain': 7.0}),
                ])),
                ('visits', 1)])),
            ('2018-03', OrderedDict([
                ('by-product', OrderedDict([
                    (u'Desk Combination', {'validated': 8, 'gain': 8.0}),
                    (u'Virtual Home Staging', {'validated': 1, 'gain': 1.0}),
                ])),
                ('visits', 1)])),
            ('2018-04', OrderedDict([
                ('by-product', OrderedDict([
                    (u'Desk Combination', {'validated': 4, 'gain': 4.0}),
                    (u'Virtual Interior Design', {'validated': 7, 'gain': 7.0}),
                ])),
                ('visits', 1)])),
            ('2018-05', {
                'by-product': {'-': {'validated': 0, 'gain': 0.0}},
                'visits': 1}),
        ]), self.affiliate.report_data())

    def test_report_with_product_restriction(self):

        self.affiliate.restriction_product_tmpl_ids |= (self.pt1 | self.pt2)

        self.affiliate.gain_type = 'fixed'
        self.affiliate.gain_value = 1
        self.create_sales()

        # Add a sale that should not even be attached to the affiliate request
        # (not a selected product)
        self.create_sale([(self.pp3, 3)], create_date='2018-05-20')

        self.assertEqual(OrderedDict([
            ('2018-01', OrderedDict([
                ('by-product', OrderedDict([
                    (u'Virtual Home Staging', {'validated': 2, 'gain': 2.0}),
                    (u'Virtual Interior Design', {'validated': 3, 'gain': 3.0}),
                ])),
                ('visits', 2)])),
            ('2018-02', OrderedDict([
                ('by-product', OrderedDict([
                    (u'Virtual Home Staging', {'validated': 7, 'gain': 7.0}),
                    (u'Virtual Interior Design', {'validated': 0, 'gain': 0.0}),
                ])),
                ('visits', 1)])),
            ('2018-03', OrderedDict([
                ('by-product', OrderedDict([
                    (u'Virtual Home Staging', {'validated': 1, 'gain': 1.0}),
                    (u'Virtual Interior Design', {'validated': 0, 'gain': 0.0}),
                ])),
                ('visits', 1)])),
            ('2018-04', OrderedDict([
                ('by-product', OrderedDict([
                    (u'Virtual Home Staging', {'validated': 0, 'gain': 0.0}),
                    (u'Virtual Interior Design', {'validated': 7, 'gain': 7.0}),
                ])),
                ('visits', 1)])),
            ('2018-05', OrderedDict([
                ('by-product', OrderedDict([
                    (u'Virtual Home Staging', {'validated': 0, 'gain': 0.0}),
                    (u'Virtual Interior Design', {'validated': 0, 'gain': 0.0}),
                ])),
                ('visits', 1)])),
        ]), self.affiliate.report_data())

    def test_report_percentage_gain_type(self):

        self.affiliate.gain_type = 'percentage'
        self.affiliate.gain_value = 10.

        self.fake_session['affiliate_request'] = self.create_affiliate_req().id
        self.create_sale([(self.pp1, 3), (self.pp2, 5)], create_date='2018-01-05')

        data = self.affiliate.report_data()

        expected_gain1 = 3 * 10./100 * self.pp1.list_price
        self.assertAlmostEqual(
            data.get('2018-01', {}).get('by-product', {}).get(
                'Virtual Interior Design', {}).get('gain', 0),
            expected_gain1)

        expected_gain2 = 5 * 10./100 * self.pp2.list_price
        self.assertAlmostEqual(
            data.get('2018-01', {}).get('by-product', {}).get(
                'Virtual Home Staging', {}).get('gain', 0),
            expected_gain2)
