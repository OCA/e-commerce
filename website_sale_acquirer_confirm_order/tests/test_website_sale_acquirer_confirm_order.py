# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged("post_install", "-at_install")
class WebsiteSaleHttpCase(HttpCase):
    def setUp(self):
        super().setUp()
        self.journal_bank = self.env["account.journal"].create(
            {
                "name": "Test WSACO",
                "code": "WSACO",
                "type": "bank",
            }
        )
        self.acquirer = self.env.ref("payment.payment_acquirer_transfer")
        self.acquirer.write(
            {
                "journal_id": self.journal_bank.id,
            }
        )

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour(
            "/shop",
            "website_sale_acquirer_confirm_order",
            login="admin",
            step_delay=100,
        )
        partner = self.env.ref("base.partner_admin")
        last_order_sent = self.env["sale.order"].search(
            [
                ("partner_id", "=", partner.id),
            ],
            order="date_order desc",
            limit=1,
        )
        self.assertEqual(last_order_sent.state, "sent")
        self.acquirer.write(
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
        partner = self.env.ref("base.partner_admin")
        last_order_confirm = self.env["sale.order"].search(
            [
                ("partner_id", "=", partner.id),
            ],
            order="date_order desc",
            limit=1,
        )
        self.assertEqual(last_order_confirm.state, "sale")
