# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestHooks(TransactionCase):

    def setUp(self):
        super(TestHooks, self).setUp()
        self.trgm_mod = self.env['trgm.index']

    def test_trgm_index_exists_product(self):
        """ Test trgm index exists on prod name """
        self.assertTrue(
            self.trgm_mod.index_exists(
                'product.template', 'name'
            )
        )
