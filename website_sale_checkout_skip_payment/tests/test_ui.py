# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import Mock, patch
import odoo.tests

@odoo.tests.tagged('post_install', '-at_install')
class TestUi(odoo.tests.HttpCase):
    def setUp(self):
        super().setUp()
        # Active skip payment for Mitchel Admin
        self.partner = self.env.ref("base.partner_admin")
        self.partner.with_context(**{"res_partner_search_mode": "customer"}).write(
            {"skip_website_checkout_payment": True}
        )
    
    def test_checkout_skip_payment(self):
        website = self.env.ref("website.website2")
        with patch("odoo.addons.website_sale_checkout_skip_payment.models.website.request", new=Mock()) as request:
            request.session.uid = False
            self.assertFalse(website.checkout_skip_payment)

    def test_ui_website(self):
        self.start_tour("/shop", "website_sale_checkout_skip_payment", login="admin")
