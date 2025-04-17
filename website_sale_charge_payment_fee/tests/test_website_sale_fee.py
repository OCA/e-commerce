# Copyright 2022 Studio73 - Miguel Gandía <miguel@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import Command
from odoo.tests import HttpCase, RecordCapturer, tagged


@tagged("post_install", "-at_install")
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
        transfer_provider = cls.env.ref("payment.payment_provider_transfer")
        transfer_provider.write(
            {
                "charge_fee": True,
                "charge_fee_product_id": cls.product_product_service.id,
                "charge_fee_type": "percentage",
                "charge_fee_percentage": 10.00,
                "state": "enabled",
                "is_published": True,
            }
        )
        transfer_provider._compute_charge_fee_description()

        payment_method = cls.env["payment.method"].create(
            {
                "name": "wire transfer2",
                "code": "wire_transfer2",
                "sequence": 1000,
                "active": True,
                "provider_ids": [Command.link(transfer_provider.id)],
            }
        )
        transfer_provider.write(
            {
                "payment_method_ids": [
                    Command.link(payment_method.id),
                ]
            }
        )
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
        cls.env["res.config.settings"].create(
            {
                "show_line_subtotals_tax_selection": "tax_excluded",
            }
        ).execute()

    def test_charge_payment_fee_percentage(self):
        with RecordCapturer(self.env["sale.order"], []) as capture:
            self.start_tour("/shop", "payment_fee_tour", login="portal")
        created_order = capture.records
        price = 10 / 100 * 99.0
        self.assertEqual(created_order.amount_payment_fee, price)

    def test_charge_payment_fee_fixed(self):
        acquirer = self.env.ref("payment.payment_provider_transfer")
        acquirer.write(
            {
                "charge_fee_type": "fixed",
                "charge_fee_fixed_price": 10.00,
                "charge_fee_currency_id": self.env.ref("base.USD").id,
            }
        )
        with RecordCapturer(self.env["sale.order"], []) as capture:
            self.start_tour("/", "payment_fee_tour", login="portal")
        created_order = capture.records
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
