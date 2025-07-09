# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.portal_sale_order_website_filter.controllers.portal import (
    CustomerPortal,
)
from odoo.addons.website.tools import MockRequest


@tagged("-at_install", "post_install")
class TestPortalSaleOrderWebsiteFilter(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website_1 = cls.env["website"].create({"name": "Test Website 1"})
        cls.website_2 = cls.env["website"].create({"name": "Test Website 2"})
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.so_1 = cls._create_sale_order(cls.partner, cls.website_1)
        cls.so_2 = cls._create_sale_order(cls.partner, cls.website_1)
        cls.so_3 = cls._create_sale_order(cls.partner, cls.website_2)

    @classmethod
    def _create_sale_order(cls, partner, website):
        sale_order = cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "website_id": website.id,
                "state": "sent",
            }
        )
        sale_order.message_subscribe([partner.id])
        return sale_order

    def get_orders(self, is_quote=False):
        portal_controller = CustomerPortal()
        if is_quote:
            domain = portal_controller._prepare_quotations_domain(self.partner)
        else:
            domain = portal_controller._prepare_orders_domain(self.partner)
        return self.env["sale.order"].search(domain)

    def test_sale_order_filtered_website_1(self):
        with MockRequest(self.env, website=self.website_1):
            orders = self.get_orders(is_quote=True)
            self.assertEqual(orders, self.so_1 | self.so_2)
            orders = self.so_1 | self.so_2 | self.so_3
            orders.state = "sale"
            orders = self.get_orders()
            self.assertEqual(orders, self.so_1 | self.so_2)

    def test_sale_order_filtered_website_2(self):
        with MockRequest(self.env, website=self.website_2):
            orders = self.get_orders(is_quote=True)
            self.assertEqual(orders, self.so_3)
            orders = self.so_1 | self.so_2 | self.so_3
            orders.state = "sale"
            orders = self.get_orders()
            self.assertEqual(orders, self.so_3)
