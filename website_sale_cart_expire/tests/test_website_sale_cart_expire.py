# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from freezegun import freeze_time

from odoo import fields
from odoo.tests import TransactionCase


class TestWebsiteSaleCartExpire(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tx_counter = 0
        # Websites
        cls.website_1 = cls.env.ref("website.default_website")
        cls.website_2 = cls.env.ref("website.website2")
        cls.website_1.cart_expire_delay = 0.00  # hours (= disabled)
        cls.website_2.cart_expire_delay = 2.00  # hours
        # Orders
        cls.order_1 = cls.env.ref("website_sale.website_sale_order_1")
        cls.order_2 = cls.env.ref("website_sale.website_sale_order_2")
        cls.order_3 = cls.env.ref("website_sale.website_sale_order_3")
        cls.order_4 = cls.env.ref("website_sale.website_sale_order_4")
        cls.orders = cls.order_1 + cls.order_2 + cls.order_3 + cls.order_4
        # Set to draft and assign all to website_2
        # (this also updates write_date to now())
        cls.orders.write({"state": "draft", "website_id": cls.website_2.id})

    def _create_payment_transaction(self, order):
        self.tx_counter += 1
        acquirer = self.env.ref("payment.payment_acquirer_test")
        return self.env["payment.transaction"].create(
            {
                "acquirer_id": acquirer.id,
                "reference": f"{order.name}-{self.tx_counter}",
                "amount": order.amount_total,
                "currency_id": order.currency_id.id,
                "partner_id": order.partner_id.id,
                "operation": "online_direct",
                "sale_order_ids": [fields.Command.set([order.id])],
            }
        )

    def test_expire_dates(self):
        # Expire Date is set in the future
        self.assertTrue(self.order_1.cart_expire_date)
        # Changing to a website without expire delay should remove it
        self.order_1.website_id = self.website_1
        self.assertFalse(self.order_1.cart_expire_date)

    def test_expire_scheduler(self):
        # Case 1: We haven't reached the expire date yet
        self.env["website"]._scheduler_website_expire_cart()
        for order in self.orders:
            self.assertEqual(order.state, "draft")
        # Case 2: We have reached website 2 expire date
        with freeze_time(datetime.now() + timedelta(hours=3)):
            self.env["website"]._scheduler_website_expire_cart()
        for order in self.orders:
            self.assertEqual(order.state, "cancel")

    def test_expire_scheduler_multi_website(self):
        # For this test, we split the orders among the 2 websites
        (self.order_1 + self.order_2).write({"website_id": self.website_1.id})
        with freeze_time(datetime.now() + timedelta(hours=3)):
            self.env["website"]._scheduler_website_expire_cart()
        self.assertEqual(self.order_1.state, "draft", "No expire delay on website 1")
        self.assertEqual(self.order_2.state, "draft", "No expire delay on website 1")
        self.assertEqual(self.order_3.state, "cancel", "Should've been cancelled")
        self.assertEqual(self.order_4.state, "cancel", "Should've been cancelled")

    @freeze_time(datetime.now() + timedelta(hours=3))
    def test_expire_scheduler_ignore_sent_quotation(self):
        """Test that sent quotations aren't cancelled

        Quotations can be sent manually or automatically when using
        wire transfer as payment. They shouldn't be cancelled.
        """
        self.order_1.action_quotation_sent()
        self.env["website"]._scheduler_website_expire_cart()
        self.assertNotEqual(self.order_1.state, "cancel")

    @freeze_time(datetime.now() + timedelta(hours=3))
    def test_expire_scheduler_ignore_in_payment(self):
        """Carts with a payment transaction in progress shouldn't expire"""
        self._create_payment_transaction(self.order_1)
        tx_2 = self._create_payment_transaction(self.order_2)
        tx_2._set_pending()
        tx_3 = self._create_payment_transaction(self.order_3)
        tx_3._set_canceled()
        tx_4 = self._create_payment_transaction(self.order_4)
        tx_4._set_error("Something went wrong")
        # Carts with transactions in progress are not canceled
        # Even those with 'draft' or 'error' transactions, because
        # the timer is reseted whenever a tx state changes.
        self.env["website"]._scheduler_website_expire_cart()
        self.assertNotEqual(self.order_1.state, "cancel")
        self.assertNotEqual(self.order_2.state, "cancel")
        self.assertNotEqual(self.order_3.state, "cancel")
        self.assertNotEqual(self.order_4.state, "cancel")
        # In case of error, another transaction can be initialized
        # However for order_1, no more activity was detected, so it's canceled
        with freeze_time(datetime.now() + timedelta(hours=3)):
            self._create_payment_transaction(self.order_4)
            self.env["website"]._scheduler_website_expire_cart()
        self.assertEqual(self.order_1.state, "cancel")
        self.assertNotEqual(self.order_4.state, "cancel")
