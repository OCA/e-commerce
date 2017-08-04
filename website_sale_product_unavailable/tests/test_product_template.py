# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.tests.common import TransactionCase


class ProductTemplateCase(TransactionCase):
    def setUp(self):
        super(ProductTemplateCase, self).setUp()
        self.Product = self.env['product.product']

    def test_compute_availability_sequence_in_stock(self):
        """It should compute the correct in_stock availability sequence"""
        in_stock_product = self.Product.create({
            'name': 'in stock',
            'type': 'service',
            'availability': 'in_stock',
        })
        self.assertEqual(in_stock_product.availability_sequence, 0)

    def test_compute_availability_sequence_warning(self):
        """It should compute the correct warning availability sequence"""
        warning_product = self.Product.create({
            'name': 'warning',
            'type': 'service',
            'availability': 'warning',
        })
        self.assertEqual(warning_product.availability_sequence, 5)

    def test_compute_availability_sequence_unavailable(self):
        """It should compute the correct unavailable availability sequence"""
        unavailable_product = self.Product.create({
            'name': 'unavailable',
            'type': 'service',
            'availability': 'unavailable',
        })
        self.assertEqual(unavailable_product.availability_sequence, 10)

    def test_compute_availability_sequence_empty(self):
        """It should compute the correct empty availability sequence"""
        empty_product = self.Product.create({
            'name': 'empty',
            'type': 'service',
            'availability': 'empty',
        })
        self.assertEqual(empty_product.availability_sequence, 20)
