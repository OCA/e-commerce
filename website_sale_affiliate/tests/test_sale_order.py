# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from mock import patch

from ..models.sale_affiliate import Affiliate
from .test_sale_common import SaleCase


class SaleOrderCase(SaleCase):
    def setUp(self):
        super(SaleOrderCase, self).setUp()

    @patch.object(Affiliate, 'find_from_session')
    def test_create_with_no_affiliate(
        self,
        find_from_session_mock,
    ):
        """Creates a sale order without an affiliate request id
        when there is no affiliate found"""
        find_from_session_mock.return_value = None

        sale_order = self.env['sale.order'].create(self.sale_order_vals)
        self.assertTrue(
            sale_order.exists(),
            'Sale order not created',
        )
        self.assertFalse(
            sale_order.affiliate_request_id.id,
            'Request ID added to sale order',
        )

    @patch.object(Affiliate, 'get_request')
    @patch.object(Affiliate, 'find_from_session')
    def test_create_affiliate_exists_but_request_invalid(
        self,
        find_from_session_mock,
        get_request_mock,
    ):
        """Creates a sale order without an affiliate request id
        when request is invalid"""
        find_from_session_mock.return_value = self.test_affiliate
        get_request_mock.return_value = None

        sale_order = self.env['sale.order'].create(self.sale_order_vals)
        self.assertTrue(
            sale_order.exists(),
            'Sale order not created',
        )
        self.assertFalse(
            sale_order.affiliate_request_id.id,
            'Request ID added to sale order',
        )

    @patch.object(Affiliate, 'get_request')
    @patch.object(Affiliate, 'find_from_session')
    def test_create_affiliate_exists_and_request_valid(
        self,
        find_from_session_mock,
        get_request_mock,
    ):
        """Adds affiliate request id to sale order when request valid"""
        find_from_session_mock.return_value = self.test_affiliate
        get_request_mock.return_value = self.test_request

        sale_order = self.env['sale.order'].create(self.sale_order_vals)
        self.assertTrue(
            sale_order.exists(),
            'Sale order not created',
        )
        self.assertEqual(
            sale_order.affiliate_request_id, self.test_request,
            'Request ID not added to sale order',
        )
