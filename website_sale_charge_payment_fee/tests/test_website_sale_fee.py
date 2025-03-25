# Copyright 2022 Studio73 - Miguel Gandía <miguel@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo.tests import new_test_user, tagged
from odoo.tests.common import HttpCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestUi(HttpCase):
    def setUp(self):
        super().setUp()
        self.product_product_service = self.env["product.product"].create(
            {
                "name": "Discount wire tranfer",
                "standard_price": 70.0,
                "list_price": 79.0,
                "sale_ok": True,
            }
        )
        # Create a wire transfer payment provider
        self.wire_transfer = self.env.ref("payment.payment_provider_transfer")
        self.wire_transfer.write(
            {
                "charge_fee": True,
                "charge_fee_product_id": self.product_product_service.id,
                "charge_fee_type": "percentage",
                "charge_fee_percentage": 10.00,
                "state": "enabled",
                "is_published": True,
            }
        )
        self.wire_transfer.onchange_charge_fee_product_id()

        # Avoid Shipping/Billing address page
        self.fee_user = new_test_user(
            self.env,
            login="fee_user",
            groups="base.group_system,"
            "base.group_erp_manager,"
            "sales_team.group_sale_manager",
        )
        self.fee_user.partner_id.write(
            {
                "street": "215 Vine St",
                "city": "Scranton",
                "zip": "18503",
                "country_id": self.env.ref("base.us").id,
                "state_id": self.env.ref("base.state_us_39").id,
                "phone": "+1 555-555-5555",
                "email": "admin@yourcompany.example.com",
            }
        )

    def test_tour(self):
        self.start_tour(
            "/shop", "website_sale_order_payment_fee_tour", login="fee_user"
        )
        created_order = self.env["sale.order"].search(
            [("partner_id", "=", self.fee_user.partner_id.id)], limit=1, order="id desc"
        )
        self.assertEqual(len(created_order), 1)

    def test_charge_payment_fee_percentage(self):
        self.start_tour(
            "/shop", "website_sale_order_payment_fee_tour", login="fee_user"
        )
        created_order = self.env["sale.order"].search(
            [("partner_id", "=", self.fee_user.partner_id.id)], limit=1, order="id desc"
        )
        self.assertEqual(len(created_order), 1)
        # Apply 10% of the product price
        price = 33 * 0.10
        self.assertEqual(created_order.amount_payment_fee, price)

    def test_charge_payment_fee_fixed(self):
        self.wire_transfer.write(
            {
                "charge_fee_type": "fixed",
                "charge_fee_fixed_price": 10.00,
                "charge_fee_currency_id": self.env.ref("base.USD").id,
            }
        )

        self.start_tour("/shop", "website_sale_order_payment_fee_tour", login="admin")
        created_order = self.env["sale.order"].search(
            [("partner_id", "=", self.fee_user.partner_id.id)], limit=1, order="id desc"
        )
        self.assertEqual(len(created_order), 1)
        price = self.wire_transfer.charge_fee_fixed_price
        if (
            self.wire_transfer.charge_fee_currency_id.id
            != created_order.pricelist_id.currency_id.id
        ):
            price = self.wire_transfer.charge_fee_currency_id._convert(
                price,
                created_order.pricelist_id.currency_id,
                created_order.company_id,
                created_order.date_order,
            )
        self.assertEqual(created_order.amount_payment_fee, price)
