import logging

from odoo.tests import HttpCase, tagged

_logger = logging.getLogger(__name__)


@tagged("-at_install", "post_install")
class TestWebsiteSaleFee(HttpCase):
    def setUp(self):
        super().setUp()
        self.fee_user = self.env["res.users"].create(
            {
                "name": "Fee User",
                "login": "fee_user",
                "email": "fee_user@example.com",
                "website_id": self.env.ref("website.default_website").id,
            }
        )
        self.env["product.product"].create(
            [
                {
                    "name": "Product Test",
                    "website_published": True,
                    "list_price": 33,
                },
                {
                    "name": "Product Service Fee",
                    "website_published": True,
                    "list_price": 0,
                },
            ]
        )

    def test_charge_payment_fee_percent(self):
        self.start_tour(
            "/shop", "website_sale_order_payment_fee_tour", login="fee_user"
        )
        created_order = self.env["sale.order"].search(
            [
                ("partner_id", "=", self.fee_user.partner_id.id),
            ],
            order="id desc",
            limit=1,
        )
        self.assertTrue(created_order, "No sale order found after the tour (percent).")
        self.assertGreater(
            created_order.amount_payment_fee,
            0.0,
            "The payment fee was not applied for percent test.",
        )

    def test_charge_payment_fee_fixed(self):
        self.start_tour(
            "/shop", "website_sale_order_payment_fee_tour", login="fee_user"
        )
        created_order = self.env["sale.order"].search(
            [
                ("partner_id", "=", self.fee_user.partner_id.id),
            ],
            order="id desc",
            limit=1,
        )
        self.assertTrue(created_order, "No sale order found after the tour (fixed).")
        self.assertGreater(
            created_order.amount_payment_fee,
            0.0,
            "The payment fee was not applied for fixed test.",
        )
