# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from mock import patch

from odoo.tests.common import TransactionCase
from odoo.addons.website_sale_search_fuzzy.controllers.main import (
    WebsiteSale
)

MOCK_CONTROL = 'odoo.addons.website_sale.controllers.main.WebsiteSale'


class TestWebsiteSale(TransactionCase):

    def setUp(self):
        super(TestWebsiteSale, self).setUp()
        self.return_value = [
            '|', '|', '|',
            ('Test', 'Test'),
            ('name', 'ilike', 'Test'),
            ('name', 'like', 'Test'),
            ('description', 'ilike', 'Test'),
            ('names', 'ilike', 'Test'),
            ('description', 'like', 'Test'),
            [1, 2, 3, 4, 5],
        ]
        self.controller = WebsiteSale()
        self.prod_b = self.env.ref(
            'product.product_product_11b_product_template'
        )

    @patch('%s._get_search_domain' % MOCK_CONTROL)
    def test_get_search_domain_not_tuple(self, mock_control):
        """ Test correct tuples changed to fuzzy domain """
        mock_control.return_value = self.return_value
        res = self.controller._get_search_domain(None, None, None)

        self.return_value[4] = ('name', '%', 'Test')
        self.assertEquals(
            res,
            self.return_value,
        )
