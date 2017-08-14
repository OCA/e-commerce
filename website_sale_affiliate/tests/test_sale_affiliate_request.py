# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from mock import patch

from .test_sale_common import SaleCase

MODEL = 'odoo.addons.website_sale_affiliate.models.sale_affiliate_request'


class AffiliateRequestCase(SaleCase):
    def setUp(self):
        super(AffiliateRequestCase, self).setUp()
        self.AffiliateRequest = self.env['sale.affiliate.request']
        self.request_header_vals = {
            'REMOTE_ADDR': 'test ip',
            'HTTP_REFERER': 'test referrer',
            'HTTP_USER_AGENT': 'test user_agent',
            'HTTP_ACCEPT_LANGUAGE': 'test accept_language',
        }

    @patch('%s.request' % MODEL)
    def test_create_from_session_key_provided(self, request_mock):
        """Returns new affiliate request record, named after key"""
        request_mock.session = {'affiliate_key': 'test name'}
        request_mock.httprequest.headers.environ = self.request_header_vals

        request = self.AffiliateRequest.create_from_session(
            self.test_affiliate,
        )
        self.assertEqual(
            request.name, 'test name',
            'Affiliate request named improperly',
        )
        self.assertEqual(
            request.affiliate_id, self.test_affiliate,
            'Affiliate request not linked to correct affiliate',
        )

    @patch('%s.request' % MODEL)
    def test_create_from_session_no_key(self, request_mock):
        """Returns new affiliate request record, named according to sequence"""
        request_mock.session = {}
        request_mock.httprequest.headers.environ = self.request_header_vals

        request = self.AffiliateRequest.create_from_session(
            self.test_affiliate,
        )
        self.assertEqual(
            request.name, '0000000001',
            'Affiliate request named improperly',
        )
        self.assertEqual(
            request.affiliate_id, self.test_affiliate,
            'Affiliate request not linked to correct affiliate',
        )

    @patch('%s.request' % MODEL)
    def test_find_from_session_key_provided(self, request_mock):
        """Returns existing affiliate request record with name matching key"""
        request_mock.session = {'affiliate_key': self.test_request.name}
        request = self.AffiliateRequest.find_from_session(self.test_affiliate)
        self.assertEqual(request, self.test_request)

    def test_conversions_qualify_valid(self):
        """Returns True when neither valid_hours nor valid_sales reached"""
        self.test_affiliate.write({
            'valid_hours': '24',
            'valid_sales': '1',
        })
        # test_affiliate has no existing sales and is less than 24 hours old
        self.assertTrue(self.test_request.conversions_qualify())

    def test_conversions_qualify_valid_negative_sales_and_hours(self):
        """Returns True when valid_sales and valid_hours are negative values"""
        self.test_affiliate.write({
            'valid_hours': '-1',
            'valid_sales': '-1',
        })
        self.assertTrue(self.test_request.conversions_qualify())

    def test_conversions_qualify_valid_negative_sales(self):
        """Returns True when valid_sales is negative value
        and valid_hours not reached"""
        self.test_affiliate.write({
            'valid_hours': '24',
            'valid_sales': '-1',
        })
        self.assertTrue(self.test_request.conversions_qualify())

    def test_conversions_qualify_valid_negative_hours(self):
        """Returns True when valid_hours is negative value
        and valid_sales not reached"""
        self.test_affiliate.write({
            'valid_hours': '-1',
            'valid_sales': '1',
        })
        self.assertTrue(self.test_request.conversions_qualify())

    def test_conversions_qualify_invalid_sales(self):
        """Returns False when valid_sales reached even if hours still valid"""
        self.test_affiliate.write({
            'valid_hours': '24',
            'valid_sales': '0',
        })
        self.assertFalse(self.test_request.conversions_qualify())

    def test_conversions_qualify_invalid_time(self):
        """Returns False when valid_hours reached even if sales still valid"""
        self.test_affiliate.write({
            'valid_hours': '0',
            'valid_sales': '1',
        })
        self.assertFalse(self.test_request.conversions_qualify())
