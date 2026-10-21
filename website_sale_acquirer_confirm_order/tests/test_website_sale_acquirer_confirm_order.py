# Copyright 2025 Tecnativa - Pilar Vargas
# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import HttpCase, TransactionCase


@tagged("post_install", "-at_install")
class WebsiteSaleHttpCase(HttpCase):
    def setUp(self):
        super().setUp()
        if self.env["ir.module.module"]._get("payment_custom").state != "installed":
            self.skipTest("Transfer provider is not installed")
        self.provider = self.env.ref("payment.payment_provider_transfer")
        self.provider.write(
            {
                "state": "enabled",
                "is_published": True,
            }
        )
        self.provider._transfer_ensure_pending_msg_is_set()
        self.partner = self.env.ref("base.partner_admin")
        # VAT required by the module website_sale_vat_required
        self.partner.vat = "US01234567891"

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour(
            "/shop",
            "website_sale_acquirer_confirm_order",
            login="admin",
            step_delay=100,
        )
        last_order_sent = self.env["sale.order"].search(
            [
                ("partner_id", "=", self.partner.id),
            ],
            order="date_order desc",
            limit=1,
        )
        self.assertEqual(last_order_sent.state, "sent")
        self.provider.write(
            {
                "confirm_order": True,
            }
        )
        self.start_tour(
            "/shop",
            "website_sale_acquirer_confirm_order",
            login="admin",
            step_delay=100,
        )
        last_order_confirm = self.env["sale.order"].search(
            [
                ("partner_id", "=", self.partner.id),
            ],
            order="date_order desc",
            limit=1,
        )
        self.assertEqual(last_order_confirm.state, "sale")


class TestPaymentTransactionConfirmOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if cls.env["ir.module.module"]._get("payment_custom").state != "installed":
            cls.skipTest(cls, "Transfer provider is not installed")
        cls.provider = cls.env.ref("payment.payment_provider_transfer")
        cls.provider.write({"state": "enabled", "confirm_order": True})
        cls.partner = cls.env["res.partner"].create({"name": "Test customer"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "list_price": 100}
        )

    def _checkout_with_transfer(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [Command.create({"product_id": self.product.id})],
            }
        )
        tx = self.env["payment.transaction"].create(
            {
                "provider_id": self.provider.id,
                "payment_method_id": self.provider.payment_method_ids[:1].id,
                "amount": order.amount_total,
                "currency_id": order.currency_id.id,
                "partner_id": self.partner.id,
                "reference": order.name,
                "sale_order_ids": [Command.set(order.ids)],
            }
        )
        # What /payment/custom/process does when the customer pays
        tx._handle_notification_data("custom", {"reference": tx.reference})
        return order, tx

    def test_confirm_order_without_reaching_confirmation_page(self):
        """The customer leaves before /shop/confirmation: post-processing the
        transaction (as the payment cron does) confirms the order."""
        order, tx = self._checkout_with_transfer()
        self.assertEqual(tx.state, "pending")
        tx._post_process()
        self.assertTrue(tx.is_post_processed)
        self.assertEqual(order.state, "sale")

    def test_no_confirm_order_disabled(self):
        self.provider.confirm_order = False
        order, tx = self._checkout_with_transfer()
        tx._post_process()
        self.assertEqual(order.state, "sent")
