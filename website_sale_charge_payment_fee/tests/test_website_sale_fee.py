# Copyright 2022 Studio73 - Miguel Gandía <miguel@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import odoo.tests
from odoo.tests.common import HttpCase


@odoo.tests.tagged("post_install", "-at_install")
class TestUi(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_product_service = cls.env["product.product"].create(
            {
                "name": "Discount wire tranfer",
                "standard_price": 70.0,
                "list_price": 79.0,
                "sale_ok": True,
            }
        )
        cls.env.ref("payment.payment_acquirer_transfer").write(
            {
                "charge_fee": True,
                "charge_fee_product_id": cls.product_product_service.id,
                "charge_fee_type": "percentage",
                "charge_fee_percentage": 10.00,
            }
        )
        cls.env.ref(
            "payment.payment_acquirer_transfer"
        ).onchange_charge_fee_product_id()
        # Avoid Shipping/Billing address page
        cls.env.ref("base.partner_admin").write(
            {
                "street": "215 Vine St",
                "city": "Scranton",
                "zip": "18503",
                "country_id": cls.env.ref("base.us").id,
                "state_id": cls.env.ref("base.state_us_39").id,
                "phone": "+1 555-555-5555",
                "email": "admin@yourcompany.example.com",
            }
        )

    def test_charge_payment_fee_percentage(self):
        existing_orders = self.env["sale.order"].search([])
        self.start_tour(
            "/shop", "website_sale_order_payment_acquirer_tour", login="admin"
        )
        created_order = self.env["sale.order"].search(
            [("id", "not in", existing_orders.ids)]
        )
        price = 10 / 100 * 99.00
        self.assertEqual(created_order.amount_payment_fee, price)

    def test_charge_payment_fee_fixed(self):
        acquirer = self.env.ref("payment.payment_acquirer_transfer")
        acquirer.write(
            {
                "charge_fee_type": "fixed",
                "charge_fee_fixed_price": 10.00,
                "charge_fee_currency_id": self.env.ref("base.USD").id,
            }
        )
        existing_orders = self.env["sale.order"].search([])
        self.start_tour(
            "/shop", "website_sale_order_payment_acquirer_tour", login="admin"
        )
        created_order = self.env["sale.order"].search(
            [("id", "not in", existing_orders.ids)]
        )
        price = acquirer.charge_fee_fixed_price
        if (
            acquirer.charge_fee_currency_id.id
            != created_order.pricelist_id.currency_id.id
        ):
            price = acquirer.charge_fee_currency_id._convert(
                price,
                created_order.pricelist_id.currency_id,
                created_order.company_id,
                created_order.date_order,
            )
        self.assertEqual(created_order.amount_payment_fee, price)
