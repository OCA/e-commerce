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
        # Ensure checkout can proceed to payment in tour tests.
        self.partner.write(
            {
                "country_id": self.env.ref("base.us").id,
                "street": "123 Test St",
                "city": "Test City",
                "zip": "12345",
                "email": "admin@example.com",
                "phone": "1234567890",
                "state_id": self.env.ref("base.state_us_1").id,
            }
        )

    def test_ui_website(self):
        """Test frontend tour."""
        desk_product = self.env["product.template"].search(
            [("name", "=", "Customizable Desk")], limit=1
        )
        if not desk_product:
            self.env["product.template"].create(
                {
                    "name": "Customizable Desk",
                    "type": "consu",
                    "list_price": 50.0,
                    "is_published": True,
                }
            )
        self.start_tour(
            "/shop",
            "website_sale_acquirer_confirm_order",
            login="admin",
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
        )
        last_order_confirm = self.env["sale.order"].search(
            [
                ("partner_id", "=", self.partner.id),
            ],
            order="date_order desc",
            limit=1,
        )
        self.assertEqual(last_order_confirm.state, "sale")
