# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase

from odoo.addons.website_quote.controllers.main import sale_quote


class TestController(TransactionCase):

    def setUp(self):
        super(TestController, self).setUp()
        self.partner = self.env.ref('portal.partner_demo_portal')
        self.product = self.env.ref('product.product_product_11')
        self.sale = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 123.45,
            })]
        })
        self.controller = sale_quote()

    def test_view_msg_help(self):
        """It should append help message into QContext."""
        res = self.controller.view(self.sale.id)
        self.assertIn('tx_msg_help', res.qcontext)

    def test_view_msg_pending(self):
        """It should append pending message into QContext."""
        res = self.controller.view(self.sale.id)
        self.assertIn('tx_msg_pending', res.qcontext)
        
    def test_view_msg_done(self):
        """It should append done message into QContext."""
        res = self.controller.view(self.sale.id)
        self.assertIn('tx_msg_done', res.qcontext)
        
    def test_view_msg_cancel(self):
        """It should append cancel message into QContext."""
        res = self.controller.view(self.sale.id)
        self.assertIn('tx_msg_cancel', res.qcontext)
        
    def test_view_msg_error(self):
        """It should append error message into QContext."""
        res = self.controller.view(self.sale.id)
        self.assertIn('tx_msg_error', res.qcontext)
