# Copyright 2022 Studio73 - Miguel Gandía <miguel@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from types import SimpleNamespace
from unittest.mock import patch

from odoo import Command
from odoo.tests import HttpCase, RecordCapturer, TransactionCase, new_test_user, tagged

from odoo.addons.website_sale_charge_payment_fee.controllers import main as fee_main


@tagged("post_install", "-at_install")
class TestPaymentFee(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].get_current_website()
        cls.partner = cls.env["res.partner"].create({"name": "Payment Fee Partner"})
        cls.fee_product = cls.env["product.product"].create(
            {
                "name": "Payment Fee",
                "sale_ok": True,
                "standard_price": 1.0,
                "list_price": 1.0,
                "taxes_id": [Command.clear()],
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Payment Fee Test Product",
                "sale_ok": True,
                "standard_price": 100.0,
                "list_price": 100.0,
                "taxes_id": [Command.clear()],
            }
        )
        cls.provider = cls.env.ref("payment.payment_provider_transfer")
        cls.provider.write(
            {
                "charge_fee": True,
                "charge_fee_product_id": cls.fee_product.id,
                "charge_fee_type": "percentage",
                "charge_fee_percentage": 10.0,
                "state": "enabled",
                "is_published": True,
            }
        )

    def _create_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "website_id": self.website.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )

    def test_update_fee_line_percentage_replaces_existing_fee(self):
        order = self._create_order()

        order.update_fee_line(self.provider)
        order.update_fee_line(self.provider)

        fee_line = order.order_line.filtered("payment_fee_line")
        self.assertEqual(len(fee_line), 1)
        self.assertEqual(fee_line.price_unit, 10.0)
        self.assertEqual(order.amount_payment_fee, 10.0)
        self.assertFalse(fee_line._show_in_cart())
        self.assertNotIn(fee_line, order.website_order_line)

    def test_update_fee_line_fixed_without_fee_removes_existing_fee(self):
        order = self._create_order()
        self.provider.write(
            {
                "charge_fee_type": "fixed",
                "charge_fee_fixed_price": 7.0,
                "charge_fee_currency_id": order.currency_id.id,
            }
        )

        order.update_fee_line(self.provider)
        self.provider.charge_fee = False
        order.update_fee_line(self.provider)

        self.assertFalse(order.order_line.filtered("payment_fee_line"))
        self.assertEqual(order.amount_payment_fee, 0.0)

    def test_update_fee_line_fixed_converts_currency(self):
        order = self._create_order()
        eur = self.env.ref("base.EUR")
        usd = self.env.ref("base.USD")
        eur.active = True
        usd.active = True
        pricelist = self.env["product.pricelist"].create(
            {
                "name": "Payment Fee EUR",
                "currency_id": eur.id,
            }
        )
        order.pricelist_id = pricelist
        self.provider.write(
            {
                "charge_fee_type": "fixed",
                "charge_fee_fixed_price": 7.0,
                "charge_fee_currency_id": usd.id,
            }
        )

        order.update_fee_line(self.provider)

        expected_price = usd._convert(7.0, eur, order.company_id, order.date_order)
        fee_line = order.order_line.filtered("payment_fee_line")
        self.assertEqual(fee_line.price_unit, expected_price)

    def test_update_fee_line_percentage_tax_included(self):
        order = self._create_order()
        self.website.show_line_subtotals_tax_selection = "tax_included"

        order.update_fee_line(self.provider)

        self.assertEqual(order.amount_payment_fee, 10.0)

    def test_charge_fee_description_without_product(self):
        provider = self.env["payment.provider"].new({"charge_fee_product_id": False})

        provider._compute_charge_fee_description()

        self.assertFalse(provider.charge_fee_description)

    def test_controller_helpers_update_fee_and_payment_context(self):
        order = self._create_order()
        request = SimpleNamespace(env=self.env)

        with patch.object(fee_main, "request", request):
            fee_main._update_order_fee_from_provider_id(order, self.provider.id)
            fee_main._update_order_fee_from_provider_id(order, False)
            fee_main._update_order_fee_from_provider_id(
                order, self.provider.id + 100000
            )

        qcontext = {}
        fee_main._update_payment_context_amount(qcontext, order)

        self.assertEqual(order.amount_payment_fee, 10.0)
        self.assertEqual(qcontext["amount"], order.amount_total)
        self.assertTrue(qcontext["access_token"])

    def test_shop_payment_updates_fee_from_provider_id(self):
        order = self._create_order()
        res = SimpleNamespace(
            qcontext={
                "payment_methods_sudo": self.env["payment.method"],
                "providers_sudo": self.provider,
            }
        )
        request = SimpleNamespace(env=self.env, cart=order)

        with (
            patch.object(fee_main, "request", request),
            patch.object(fee_main.WebsiteSale, "shop_payment", return_value=res),
        ):
            result = fee_main.WebsiteSaleFee.shop_payment.original_endpoint(
                fee_main.WebsiteSaleFee(),
                provider_id=str(self.provider.id),
            )

        self.assertIs(result, res)
        self.assertEqual(order.amount_payment_fee, 10.0)
        self.assertEqual(res.qcontext["selected_provider"], self.provider)
        self.assertEqual(res.qcontext["amount"], order.amount_total)

    def test_shop_payment_updates_fee_from_payment_method(self):
        order = self._create_order()
        payment_method = self.env["payment.method"].create(
            {
                "name": "Payment Fee Method",
                "code": "payment_fee_method",
                "provider_ids": [Command.link(self.provider.id)],
            }
        )
        res = SimpleNamespace(
            qcontext={
                "payment_methods_sudo": payment_method,
                "providers_sudo": self.provider,
            }
        )
        request = SimpleNamespace(env=self.env, cart=order)

        with (
            patch.object(fee_main, "request", request),
            patch.object(fee_main.WebsiteSale, "shop_payment", return_value=res),
        ):
            fee_main.WebsiteSaleFee.shop_payment.original_endpoint(
                fee_main.WebsiteSaleFee(),
                payment_option_id=str(payment_method.id),
            )

        self.assertEqual(res.qcontext["selected_payment_method"], payment_method.id)
        self.assertEqual(res.qcontext["selected_provider"], self.provider)
        self.assertEqual(order.amount_payment_fee, 10.0)

    def test_shop_payment_selects_single_payment_method(self):
        order = self._create_order()
        payment_method = self.env["payment.method"].create(
            {
                "name": "Single Payment Fee Method",
                "code": "single_payment_fee_method",
                "provider_ids": [Command.link(self.provider.id)],
            }
        )
        res = SimpleNamespace(
            qcontext={
                "payment_methods_sudo": payment_method,
                "providers_sudo": self.provider,
            }
        )
        request = SimpleNamespace(env=self.env, cart=order)

        with (
            patch.object(fee_main, "request", request),
            patch.object(fee_main.WebsiteSale, "shop_payment", return_value=res),
        ):
            fee_main.WebsiteSaleFee.shop_payment.original_endpoint(
                fee_main.WebsiteSaleFee()
            )

        self.assertEqual(res.qcontext["selected_payment_method"], payment_method.id)
        self.assertEqual(order.amount_payment_fee, 10.0)

    def test_shop_payment_without_provider_keeps_context(self):
        order = self._create_order()
        res = SimpleNamespace(qcontext={})
        request = SimpleNamespace(env=self.env, cart=order)

        with (
            patch.object(fee_main, "request", request),
            patch.object(fee_main.WebsiteSale, "shop_payment", return_value=res),
        ):
            result = fee_main.WebsiteSaleFee.shop_payment.original_endpoint(
                fee_main.WebsiteSaleFee()
            )

        self.assertIs(result, res)
        self.assertNotIn("selected_provider", res.qcontext)

    def test_process_express_checkout_updates_fee(self):
        order = self._create_order()
        request = SimpleNamespace(env=self.env, cart=order)

        with (
            patch.object(fee_main, "request", request),
            patch.object(
                fee_main.WebsiteSale,
                "process_express_checkout",
                return_value="processed",
            ) as super_process,
        ):
            result = fee_main.WebsiteSaleFee.process_express_checkout.original_endpoint(
                fee_main.WebsiteSaleFee(),
                {"name": "Partner"},
                provider_id=str(self.provider.id),
            )

        self.assertEqual(result, "processed")
        self.assertEqual(order.amount_payment_fee, 10.0)
        super_process.assert_called_once()

    def test_get_express_shop_payment_values_updates_amounts(self):
        order = self._create_order()
        request = SimpleNamespace(env=self.env)
        values = {"providers_sudo": self.provider}

        with (
            patch.object(fee_main, "request", request),
            patch.object(
                fee_main.Cart,
                "_get_express_shop_payment_values",
                return_value=values,
            ),
        ):
            result = fee_main.WebsiteSaleFeeCart()._get_express_shop_payment_values(
                order
            )

        self.assertIs(result, values)
        self.assertEqual(order.amount_payment_fee, 10.0)
        self.assertEqual(result["amount"], order.amount_total)
        self.assertEqual(
            result["minor_amount"],
            fee_main.payment_utils.to_minor_currency_units(
                order._get_amount_total_excluding_delivery(), order.currency_id
            ),
        )

    def test_get_express_shop_payment_values_without_provider(self):
        order = self._create_order()
        request = SimpleNamespace(env=self.env)
        values = {}

        with (
            patch.object(fee_main, "request", request),
            patch.object(
                fee_main.Cart,
                "_get_express_shop_payment_values",
                return_value=values,
            ),
        ):
            result = fee_main.WebsiteSaleFeeCart()._get_express_shop_payment_values(
                order
            )

        self.assertIs(result, values)
        self.assertNotIn("amount", result)

    def test_shop_payment_transaction_updates_fee(self):
        order = self._create_order()
        request = SimpleNamespace(env=self.env)

        with (
            patch.object(fee_main, "request", request),
            patch.object(
                fee_main.PaymentPortal,
                "shop_payment_transaction",
                return_value={"status": "ok"},
            ) as super_transaction,
        ):
            shop_payment_transaction = (
                fee_main.WebsiteSaleFeePaymentPortal.shop_payment_transaction
            )
            endpoint = shop_payment_transaction.original_endpoint
            result = endpoint(
                fee_main.WebsiteSaleFeePaymentPortal(),
                order.id,
                "access-token",
                provider_id=str(self.provider.id),
            )

        self.assertEqual(result, {"status": "ok"})
        self.assertEqual(order.amount_payment_fee, 10.0)
        super_transaction.assert_called_once()


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
        cls.product_product_buy = cls.env["product.template"].create(
            {
                "name": "Test-1",
                "standard_price": 33.0,
                "list_price": 33.0,
                "is_published": True,
                "sale_ok": True,
                "taxes_id": [Command.clear()],
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
        payment_method = cls.env["payment.method"].create(
            {
                "name": "wire transfer2",
                "code": "wire_transfer2",
                "sequence": 1000,
                "active": True,
                "provider_ids": [Command.link(transfer_provider.id)],
            }
        )
        transfer_provider.payment_method_ids = [Command.set([payment_method.id])]
        cls.portal_login = "payment_fee_portal"
        portal_user = new_test_user(
            cls.env,
            login=cls.portal_login,
            password=cls.portal_login,
            groups="base.group_portal",
        )
        # Avoid Shipping/Billing address page
        portal_user.partner_id.write(
            {
                "street": "215 Vine St",
                "city": "Scranton",
                "zip": "18503",
                "country_id": cls.env.ref("base.us").id,
                "state_id": cls.env.ref("base.state_us_39").id,
                "phone": "+1 555-555-5555",
                "vat": "41511545146",
            }
        )
        cls.env["res.config.settings"].create(
            {
                "show_line_subtotals_tax_selection": "tax_excluded",
            }
        ).execute()

    def test_charge_payment_fee_percentage(self):
        with RecordCapturer(self.env["sale.order"], []) as capture:
            self.start_tour("/shop", "payment_fee_tour", login=self.portal_login)
        created_order = capture.records
        price = 10 / 100 * 99.0
        self.assertEqual(created_order.amount_payment_fee, price)

    def test_charge_payment_fee_fixed(self):
        provider = self.env.ref("payment.payment_provider_transfer")
        provider.write(
            {
                "charge_fee_type": "fixed",
                "charge_fee_fixed_price": 10.00,
                "charge_fee_currency_id": self.env.ref("base.USD").id,
            }
        )
        with RecordCapturer(self.env["sale.order"], []) as capture:
            self.start_tour("/", "payment_fee_tour", login=self.portal_login)
        created_order = capture.records
        price = provider.charge_fee_fixed_price
        if (
            provider.charge_fee_currency_id.id
            != created_order.pricelist_id.currency_id.id
        ):
            price = provider.charge_fee_currency_id._convert(
                price,
                created_order.pricelist_id.currency_id,
                created_order.company_id,
                created_order.date_order,
            )
        self.assertEqual(created_order.amount_payment_fee, price)
