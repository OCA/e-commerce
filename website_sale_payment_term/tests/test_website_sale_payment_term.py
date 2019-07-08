# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestWebsiteSalePaymentTerm(TransactionCase):

    post_install = True
    at_install = False

    def test_website_sale_payment_term(self):
        """ The testing workflow is the following:
        1) Create 2 payment acquirers with 2 different payment terms
        2) Create 4 sale orders, 2 of them website orders, all of them should
        have payment terms
        3) Verify that the website orders have the proper payment terms
        4) Make a various changes on the orders and verify that the terms are
        set correctly.
        """
        model_payment_acquirer = self.env['payment.acquirer']
        model_account_payment_term = self.env['account.payment.term']
        model_sale_order = self.env['sale.order']
        model_res_partner = self.env['res.partner']
        customer1 = model_res_partner.create({'name': 'customer1'})
        term1 = model_account_payment_term.create({
            'name': 'test term1',
        })
        term2 = model_account_payment_term.create({
            'name': 'term2',
        })
        term3 = model_account_payment_term.create({
            'name': 'term3',
        })
        acquirer1 = model_payment_acquirer.create({
            'name': 'acquirer1',
            'payment_term_id': term1.id,
            'view_template_id': self.env.ref(
                'payment.default_acquirer_button').id,
        })
        acquirer2 = model_payment_acquirer.create({
            'name': 'acquirer2',
            'payment_term_id': term2.id,
            'view_template_id': self.env.ref(
                'payment.default_acquirer_button').id,
        })
        acquirer3 = model_payment_acquirer.create({
            'name': 'acquirer3',
            'payment_term_id': term3.id,
            'view_template_id': self.env.ref(
                'payment.default_acquirer_button').id,
        })
        sale1 = model_sale_order.create({
            'partner_id': customer1.id,
        })
        sale2 = model_sale_order.create({
            'partner_id': customer1.id,
        })
        sale3 = model_sale_order.create({
            'partner_id': customer1.id,
            'payment_acquirer_id': acquirer1.id,
        })
        sale4 = model_sale_order.create({
            'partner_id': customer1.id,
            'payment_acquirer_id': acquirer2.id,
        })
        self.assertFalse(sale1.payment_acquirer_id)
        self.assertFalse(sale1.payment_term_id)
        self.assertFalse(sale2.payment_acquirer_id)
        self.assertFalse(sale2.payment_term_id)
        self.assertEquals(sale3.payment_acquirer_id.id, acquirer1.id)
        self.assertEquals(
            sale3.payment_term_id.id,
            acquirer1.payment_term_id.id,
        )
        self.assertEquals(sale4.payment_acquirer_id.id, acquirer2.id)
        self.assertEquals(
            sale4.payment_term_id.id,
            acquirer2.payment_term_id.id,
        )
        (sale3 + sale4).write({'payment_acquirer_id': acquirer3.id})
        self.assertEquals(sale3.payment_acquirer_id.id, acquirer3.id)
        self.assertEquals(
            sale3.payment_term_id.id,
            acquirer3.payment_term_id.id,
        )
        self.assertEquals(sale4.payment_acquirer_id.id, acquirer3.id)
        self.assertEquals(
            sale4.payment_term_id.id,
            acquirer3.payment_term_id.id,
        )
