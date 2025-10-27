# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import tagged
from odoo.tests.common import HttpCase


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
