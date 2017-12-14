# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from mock import patch
from odoo.http import Response
from odoo.tests.common import TransactionCase
from ..controllers.main import WebsiteSaleSelectQty

CONTROLLER_PATH = 'odoo.addons.website_sale_select_qty.controllers.main'
REQUEST_PATH = CONTROLLER_PATH + '.request'
SUPER_PATH = CONTROLLER_PATH + '.WebsiteSale.product'


@patch(REQUEST_PATH)
class TestWebsiteSaleSelectQty(TransactionCase):

    def setUp(self):
        super(TestWebsiteSaleSelectQty, self).setUp()

        self.test_controller = WebsiteSaleSelectQty()

        # Needed when tests are run with no prior requests (e.g. on install)
        base_request_patcher = patch('odoo.http.request')
        self.addCleanup(base_request_patcher.stop)
        base_request_patcher.start()

        super_patcher = patch(SUPER_PATH)
        self.addCleanup(super_patcher.stop)
        super_mock = super_patcher.start()
        super_mock.return_value = Response(qcontext={})

    def test_product_no_quantity(self, request_mock):
        """It should set quantity to 1 when no quantity param provided"""
        request_mock.params = {}
        test_result = self.test_controller.product().qcontext['quantity']

        self.assertEqual(test_result, '1')

    def test_product_invalid_quantity(self, request_mock):
        """It should set quantity to 1 when invalid quantity param provided"""
        request_mock.params = {'quantity': 'Invalid'}
        test_result = self.test_controller.product().qcontext['quantity']

        self.assertEqual(test_result, '1')

    def test_product_integer_quantity(self, request_mock):
        """It should preserve integer quantity param values"""
        request_mock.params = {'quantity': '3'}
        test_result = self.test_controller.product().qcontext['quantity']

        self.assertEqual(test_result, '3')

    def test_product_decimal_quantity(self, request_mock):
        """It should preserve decimal quantity param values"""
        request_mock.params = {'quantity': '3.24'}
        test_result = self.test_controller.product().qcontext['quantity']

        self.assertEqual(test_result, '3.24')

    def test_product_clean_up_decimal_quantity(self, request_mock):
        """It should convert decimal quantities into integers where possible"""
        request_mock.params = {'quantity': '3.00'}
        test_result = self.test_controller.product().qcontext['quantity']

        self.assertEqual(test_result, '3')
