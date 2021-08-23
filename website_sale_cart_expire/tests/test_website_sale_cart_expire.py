# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

import mock

from odoo.tests import common


class TestWebsiteSaleCartExpire(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        with mock.patch("odoo.fields.Datetime.now") as mock_now:
            mock_now.return_value = datetime.now() + timedelta(hours=3)
            self.env["website"]._scheduler_website_expire_cart()
        for order in self.orders:
            self.assertEqual(order.state, "cancel")

    def test_expire_scheduler_multi_website(self):
        # For this test, we split the orders among the 2 websites
        (self.order_1 + self.order_2).write({"website_id": self.website_1.id})
        with mock.patch("odoo.fields.Datetime.now") as mock_now:
            mock_now.return_value = datetime.now() + timedelta(hours=3)
            self.env["website"]._scheduler_website_expire_cart()
        self.assertEqual(self.order_1.state, "draft", "No expire delay on website 1")
        self.assertEqual(self.order_2.state, "draft", "No expire delay on website 1")
        self.assertEqual(self.order_3.state, "cancel", "Should've been cancelled")
        self.assertEqual(self.order_4.state, "cancel", "Should've been cancelled")
