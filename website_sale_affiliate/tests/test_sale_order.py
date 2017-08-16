# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from mock import patch

from ..models.sale_affiliate_request import AffiliateRequest
from .test_sale_common import SaleCase


class SaleOrderCase(SaleCase):
    def setUp(self):
        super(SaleOrderCase, self).setUp()

    @patch.object(AffiliateRequest, 'current_qualified')
    def test_create_calls_current_qualified(self, current_qualified_mock):
        """Calls current_qualified() on sale.affiliate.request model"""
        current_qualified_mock.return_value = None
        self.env['sale.order'].create(self.sale_order_vals)
        current_qualified_mock.assert_called_once_with()

    @patch.object(AffiliateRequest, 'current_qualified')
    def test_create_adds_none(self, current_qualified_mock):
        """Sets affiliate_request_id to False when no current qualified
        affiliate request"""
        current_qualified_mock.return_value = None
        sale_order = self.env['sale.order'].create(self.sale_order_vals)
        self.assertTrue(sale_order.exists(), 'Sale order not created')
        self.assertFalse(
            sale_order.affiliate_request_id,
            'Sale order not created properly',
        )

    @patch.object(AffiliateRequest, 'current_qualified')
    def test_create_adds_affiliate_request_id(self, current_qualified_mock):
        """Adds id of qualified affiliate request to sale order"""
        current_qualified_mock.return_value = self.demo_request
        sale_order = self.env['sale.order'].create(self.sale_order_vals)
        self.assertTrue(sale_order.exists(), 'Sale order not created')
        self.assertEqual(
            sale_order.affiliate_request_id,
            self.demo_request,
            'Request ID not added to sale order',
        )
