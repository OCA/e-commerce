# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from mock import patch

from ..models.sale_affiliate_request import AffiliateRequest
from .test_sale_common import SaleCase

MODEL = 'odoo.addons.website_sale_affiliate.models.sale_affiliate'


class AffiliateCase(SaleCase):
    def setUp(self):
        super(AffiliateCase, self).setUp()
        self.Affiliate = self.env['sale.affiliate']

    def test_default_sequence_id(self):
        """Sets sequence_id to provided sequence record by default"""
        seq_affiliate = self.Affiliate.create({
            'name': 'sequence test affiliate',
            'company_id': self.test_company.id,
            'valid_hours': -1,
            'valid_sales': -1,
        })
        sequence = self.env.ref('website_sale_affiliate.request_sequence')
        self.assertEqual(seq_affiliate.sequence_id, sequence)

    @patch('%s.request' % MODEL)
    def test_find_from_session_id_provided(self, request_mock):
        """Returns affiliate record matching affiliate_id from session"""
        request_mock.session = {'affiliate_id': self.test_affiliate.id}
        affiliate = self.Affiliate.find_from_session()
        self.assertEqual(affiliate, self.test_affiliate)

    @patch('%s.request' % MODEL)
    def test_find_from_session_id_absent(self, request_mock):
        """Returns None when id is absent from session"""
        request_mock.session = {}
        affiliate = self.Affiliate.find_from_session()
        self.assertIsNone(affiliate)

    @patch.object(AffiliateRequest, 'conversions_qualify')
    @patch.object(AffiliateRequest, 'find_from_session')
    @patch('%s.request' % MODEL)
    def test_get_request_conversions_qualify(
        self,
        request_mock,
        find_from_session_mock,
        conversions_qualify_mock,
    ):
        """It should add the appropriate affiliate request id to sale order
        when sale is a qualified conversion"""
        find_from_session_mock.return_value = self.test_request
        conversions_qualify_mock.return_value = True

        request = self.test_affiliate.get_request()
        self.assertEqual(request, self.test_request)

    @patch.object(AffiliateRequest, 'conversions_qualify')
    @patch.object(AffiliateRequest, 'find_from_session')
    @patch('%s.request' % MODEL)
    def test_get_request_conversions_do_not_qualify(
        self,
        request_mock,
        find_from_session_mock,
        conversions_qualify_mock,
    ):
        """It should not add an affiliate request id to sale order
        when sale is an unqualified conversion"""
        find_from_session_mock.return_value = self.test_request
        conversions_qualify_mock.return_value = False

        request = self.test_affiliate.get_request()
        self.assertIsNone(request)

    @patch.object(AffiliateRequest, 'create_from_session')
    @patch.object(AffiliateRequest, 'find_from_session')
    @patch('%s.request' % MODEL)
    def test_get_request_call_find_from_session(
        self,
        request_mock,
        find_from_session_mock,
        create_from_session_mock,
    ):
        """Calls find_from_session method and returns its result
        when matching request exists"""
        find_from_session_mock.return_value = self.test_request
        create_from_session_mock.return_value = None

        request = self.test_affiliate.get_request()
        find_from_session_mock.assert_called_once()
        create_from_session_mock.assert_not_called()
        self.assertEqual(request, self.test_request)

    @patch.object(AffiliateRequest, 'create_from_session')
    @patch.object(AffiliateRequest, 'find_from_session')
    @patch('%s.request' % MODEL)
    def test_get_request_call_create_from_session(
        self,
        request_mock,
        find_from_session_mock,
        create_from_session_mock,
    ):
        """Calls create_from_session method and returns its result
        when find_from_session method returns None"""
        find_from_session_mock.return_value = None
        create_from_session_mock.return_value = self.test_request

        request = self.test_affiliate.get_request()
        find_from_session_mock.assert_called_once()
        create_from_session_mock.assert_called_once()
        self.assertEqual(request, self.test_request)
