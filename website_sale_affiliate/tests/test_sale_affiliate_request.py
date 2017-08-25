# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from mock import patch

from ..models.sale_affiliate_request import AffiliateRequest
from .common import SaleCase

MODEL_PATH = 'odoo.addons.website_sale_affiliate.models.sale_affiliate_request'


class AffiliateRequestCase(SaleCase):
    def setUp(self):
        super(AffiliateRequestCase, self).setUp()
        self.AffiliateRequest = self.env['sale.affiliate.request']
        self.test_affiliate = self.env['sale.affiliate'].create({
            'name': 'test_affiliate',
            'company_id': self.demo_company.id,
            'valid_hours': 24,
            'valid_sales': 1,
        })
        self.test_request = self.env['sale.affiliate.request'].create({
            'name': 'test_request',
            'affiliate_id': self.test_affiliate.id,
            'ip': 'test ip',
            'referrer': 'test referrer',
            'user_agent': 'test user_agent',
            'accept_language': 'test language',
        })

    @patch('%s.request' % MODEL_PATH)
    def test_defaults_all_present(self, request_mock):
        ip = '0.0.0.0'
        referrer = 'referrer'
        user_agent = 'user_agent'
        accept_language = 'esperanto'
        request_mock.httprequest.headers.environ = {
            'REMOTE_ADDR': ip,
            'HTTP_REFERER': referrer,
            'HTTP_USER_AGENT': user_agent,
            'HTTP_ACCEPT_LANGUAGE': accept_language,
        }
        affiliate_request = self.env['sale.affiliate.request'].create({
            'name': 'test_headers_request',
            'affiliate_id': self.test_affiliate.id,
        })
        self.assertTrue(affiliate_request.exists())
        self.assertEqual(affiliate_request.ip, ip)
        self.assertEqual(affiliate_request.referrer, referrer)
        self.assertEqual(affiliate_request.user_agent, user_agent)
        self.assertEqual(affiliate_request.accept_language, accept_language)

    def test_conversions_qualify_valid(self):
        """Returns True when neither valid_hours nor valid_sales reached"""
        self.test_affiliate.write({
            'valid_hours': '24',
            'valid_sales': '1',
        })
        # test_affiliate has no existing sales and is less than 24 hours old
        self.assertTrue(self.test_request._conversions_qualify())

    def test_conversions_qualify_valid_negative_sales_and_hours(self):
        """Returns True when valid_sales and valid_hours are negative values"""
        self.test_affiliate.write({
            'valid_hours': '-1',
            'valid_sales': '-1',
        })
        self.assertTrue(self.test_request._conversions_qualify())

    def test_conversions_qualify_valid_negative_sales(self):
        """Returns True when valid_sales is negative value
        and valid_hours not reached"""
        self.test_affiliate.write({
            'valid_hours': '24',
            'valid_sales': '-1',
        })
        self.assertTrue(self.test_request._conversions_qualify())

    def test_conversions_qualify_valid_negative_hours(self):
        """Returns True when valid_hours is negative value
        and valid_sales not reached"""
        self.test_affiliate.write({
            'valid_hours': '-1',
            'valid_sales': '1',
        })
        self.assertTrue(self.test_request._conversions_qualify())

    def test_conversions_qualify_invalid_sales(self):
        """Returns False when valid_sales reached even if hours still valid"""
        self.test_affiliate.write({
            'valid_hours': '24',
            'valid_sales': '0',
        })
        self.assertFalse(self.test_request._conversions_qualify())

    def test_conversions_qualify_invalid_time(self):
        """Returns False when valid_hours reached even if sales still valid"""
        self.test_affiliate.write({
            'valid_hours': '0',
            'valid_sales': '1',
        })
        self.assertFalse(self.test_request._conversions_qualify())

    @patch('%s.request' % MODEL_PATH)
    def test_current_qualified_no_request_in_session(self, request_mock):
        """Returns None if no affiliate request is in session"""
        request_mock.session = {}
        self.assertIsNone(self.AffiliateRequest.current_qualified())

    @patch.object(AffiliateRequest, '_conversions_qualify')
    @patch('%s.request' % MODEL_PATH)
    def test_current_qualified_request_in_session_calls_conversions_qualify(
        self,
        request_mock,
        _conversions_qualify_mock,
    ):
        """Calls _conversions_qualify if affiliate request is in session"""
        request_mock.session = {'affiliate_request': self.test_request.id}
        self.AffiliateRequest.current_qualified()
        _conversions_qualify_mock.assert_called_once_with()

    @patch('%s.request' % MODEL_PATH)
    def test_current_qualified_request_not_in_session_returns_none(
        self,
        request_mock,
    ):
        """Returns None if no affiliate request in session"""
        request_mock.session = {}
        request = self.AffiliateRequest.current_qualified()
        self.assertIsNone(request)

    @patch.object(AffiliateRequest, '_conversions_qualify')
    @patch('%s.request' % MODEL_PATH)
    def test_current_qualified_request_in_session_returns_request(
        self,
        request_mock,
        _conversions_qualify_mock,
    ):
        """Returns affiliate request in session if its conversions qualify"""
        request_mock.session = {'affiliate_request': self.test_request.id}
        _conversions_qualify_mock.return_value = True
        request = self.AffiliateRequest.current_qualified()
        self.assertEqual(request, self.test_request)

    @patch.object(AffiliateRequest, '_conversions_qualify')
    @patch('%s.request' % MODEL_PATH)
    def test_current_qualified_request_in_session_returns_none(
        self,
        request_mock,
        _conversions_qualify_mock,
    ):
        """Returns None if conversions do not qualify for affiliate request
        currently in session"""
        request_mock.session = {'affiliate_request': self.test_request.id}
        _conversions_qualify_mock.return_value = False
        request = self.AffiliateRequest.current_qualified()
        self.assertIsNone(request)
