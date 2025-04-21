import logging

from odoo.tests import HttpCase, tagged

_logger = logging.getLogger(__name__)


@tagged("-at_install", "post_install")
class TestWebsiteSaleFee(HttpCase):
    def setUp(self):
        super().setUp()

        self.website = self.env.ref("website.default_website")
        self.fee_user = self.env["res.users"].create(
            {
                "name": "Fee User",
                "login": "fee_user",
                "email": "fee_user@example.com",
                "password": "fee_user",
                "website_id": self.website.id,
            }
        )

        self.sale_product = self.env["product.product"].create(
            {
                "name": "Product Test",
                "website_published": True,
                "list_price": 33,
            }
        )
        self.fee_product = self.env["product.product"].create(
            {
                "name": "Product Service Fee",
                "type": "service",
                "list_price": 0,
            }
        )

        self.provider = self.env.ref("payment.payment_provider_demo").sudo()
        self.provider.write(
            {
                "state": "enabled",
                "charge_fee": True,
                "charge_fee_product_id": self.fee_product.id,
            }
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _run_tour_and_assert(self):
        self.start_tour(
            "/shop", "website_sale_order_payment_fee_tour", login="fee_user"
        )

        order = self.env["sale.order"].search(
            [("partner_id", "=", self.fee_user.partner_id.id)],
            order="id desc",
            limit=1,
        )
        self.assertTrue(order, "The tour did not create an order.")
        self.assertGreater(
            order.amount_payment_fee, 0.0, "The payment surcharge was not applied."
        )
        return order

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------
    def test_charge_payment_fee_percent(self):
        self.provider.write(
            {
                "charge_fee_type": "percentage",
                "charge_fee_percentage": 5.0,
            }
        )
        self._run_tour_and_assert()

    def test_charge_payment_fee_fixed(self):
        self.provider.write(
            {
                "charge_fee_type": "fixed",
                "charge_fee_fixed_price": 2.0,
                "charge_fee_currency_id": self.env.company.currency_id.id,
            }
        )
        self._run_tour_and_assert()
