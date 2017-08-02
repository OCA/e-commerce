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
        self.assertEqual(
            order,
            'website_published desc,'
            'availability_sequence asc,'
            'availability_warning asc,'
            'website_sequence desc,'
            'id desc',
            'Availability not added to search order',
        )
