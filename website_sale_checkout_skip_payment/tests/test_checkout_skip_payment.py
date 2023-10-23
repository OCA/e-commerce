# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import Mock, patch

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class WebsiteSaleHttpCase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        # Active skip payment for Mitchel Admin
        cls.partner = cls.env.ref("base.partner_demo_portal")
        # Ensure compatibility with `website_sale_vat_required`
        cls.partner.vat = "F4K3V47"
        cls.partner.skip_website_checkout_payment = True
        cls.partner_orders = cls.partner.sale_order_ids

    def test_checkout_skip_payment(self):
        website = self.env.ref("website.website2")
        with patch(
            "odoo.addons.website_sale_checkout_skip_payment.models.website.request",
            new=Mock(),
        ) as request:
            request.session.uid = False
            self.assertFalse(website.checkout_skip_payment)

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour("/shop", "website_sale_checkout_skip_payment", login="portal")
        # Get the order created on the tour
        sale = self.partner.sale_order_ids - self.partner_orders
        self.assertEqual(sale.state, "sale")
