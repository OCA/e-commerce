# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from mock import patch

from .common import SaleCase

MODULE_PATH = 'odoo.addons.website_sale_affiliate'
AFFILIATE_REQUEST_PATH = MODULE_PATH + '.models.sale_affiliate_request'


class AffiliateCase(SaleCase):
    def setUp(self):
        super(AffiliateCase, self).setUp()
        self.Affiliate = self.env['sale.affiliate']

    def test_compute_conversion_rate_with_requests(self):
        """Computes conversion rate for affiliate with requests"""
        requests = self.demo_affiliate.request_ids
        conversions = requests.filtered(lambda r: len(r.sale_ids) > 0)
        conversion_rate = float(len(conversions)) / float(len(requests))
        self.assertAlmostEqual(
            conversion_rate,
            self.demo_affiliate.conversion_rate,
            4,
        )

    def test_compute_conversion_rate_no_requests(self):
        """Sets conversion rate to 0 for affiliate with no requests"""
        test_affiliate = self.env['sale.affiliate'].create({
            'name': 'test_affiliate',
            'company_id': self.demo_company.id,
            'valid_hours': 24,
            'valid_sales': 1,
        })
        self.assertAlmostEqual(0.0, test_affiliate.conversion_rate, 4)

    def test_compute_sales_per_request_with_requests(self):
        """Computes sales per request for affiliate with requests"""
        requests = self.demo_affiliate.request_ids
        sales_count = sum(len(request.sale_ids) for request in requests)
        sales_per_request = float(sales_count) / float(len(requests))
        self.assertAlmostEqual(
            sales_per_request,
            self.demo_affiliate.sales_per_request,
            4,
        )

    def test_compute_sales_per_request_no_requests(self):
        """Sets sales per request to 0 for affiliate with no requests"""
        test_affiliate = self.env['sale.affiliate'].create({
            'name': 'test_affiliate',
            'company_id': self.demo_company.id,
            'valid_hours': 24,
            'valid_sales': 1,
        })
        self.assertAlmostEqual(0.0, test_affiliate.sales_per_request, 4)

    def test_default_sequence_id(self):
        """Sets sequence_id to provided sequence record by default"""
        seq_affiliate = self.Affiliate.create({
            'name': 'sequence test affiliate',
            'company_id': self.demo_company.id,
            'valid_hours': -1,
            'valid_sales': -1,
        })
        sequence = self.env.ref('website_sale_affiliate.request_sequence')
        self.assertEqual(seq_affiliate.sequence_id, sequence)

    def test_find_from_kwargs_aff_ref_present(self):
        """Returns affiliate record matching aff_ref from kwargs"""
        kwargs = {'aff_ref': self.demo_affiliate}
        affiliate = self.Affiliate.find_from_kwargs(**kwargs)
        self.assertEqual(affiliate, self.demo_affiliate)

    def test_find_from_kwargs_aff_ref_absent(self):
        """Returns None when aff_ref is absent from kwargs"""
        kwargs = {}
        affiliate = self.Affiliate.find_from_kwargs(**kwargs)
        self.assertIsNone(affiliate)

    def test_find_from_kwargs_aff_ref_invalid(self):
        """Returns None when aff_ref is not an integer"""
        kwargs = {'aff_ref': 'not_int'}
        affiliate = self.Affiliate.find_from_kwargs(**kwargs)
        self.assertIsNone(affiliate)

    def test_get_request_aff_key_present_and_request_exists(self):
        """Returns existing affiliate request record matching aff_key
        from kwargs when match already exists"""
        kwargs = {'aff_key': self.demo_request.name}
        request = self.demo_affiliate.get_request(**kwargs)
        self.assertEqual(request, self.demo_request)
        self.assertEqual(
            request.affiliate_id, self.demo_affiliate,
            'Affiliate request not linked to correct affiliate',
        )

    @patch('%s.request' % AFFILIATE_REQUEST_PATH)
    def test_get_request_aff_key_present_request_missing(self, request_mock):
        """Creates and returns affiliate request record matching aff_key
        from kwargs when match does not exist"""
        test_name = 'test_request_new'
        kwargs = {'aff_key': test_name}
        request = self.demo_affiliate.get_request(**kwargs)
        self.assertTrue(request.exists(), 'Affiliate request not created')
        self.assertEqual(
            request.name, test_name,
            'Affiliate request not created with aff_key name',
        )
        self.assertEqual(
            request.affiliate_id, self.demo_affiliate,
            'Affiliate request not linked to correct affiliate',
        )

    @patch('%s.request' % AFFILIATE_REQUEST_PATH)
    def test_get_request_aff_key_missing(self, request_mock):
        """Creates and returns affiliate request record with sequential name
        when match does not exist"""
        kwargs = {}
        request = self.demo_affiliate.get_request(**kwargs)
        self.assertTrue(request.exists(), 'Affiliate request not created')
        self.assertEqual(
            request.name, '0000000001',
            'Affiliate request named improperly',
        )
        self.assertEqual(
            request.affiliate_id, self.demo_affiliate,
            'Affiliate request not linked to correct affiliate',
        )
