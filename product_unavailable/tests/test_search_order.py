# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from ..controllers.main import SearchOrder
from odoo.tests.common import TransactionCase


class SearchOrderCase(TransactionCase):
    def setUp(self):
        super(SearchOrderCase, self).setUp()
        self.SearchOrder = SearchOrder()

    def test_get_search_order(self):
        post = {}
        order = self.SearchOrder._get_search_order(post)
        order_list = order.split(',')
        self.assertIn(
            'availability_sequence asc', order_list,
            'Availability not added to search order',
        )
