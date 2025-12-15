# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import Mock, patch

import odoo.tests

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@odoo.tests.tagged("post_install", "-at_install")
class WebsiteSaleHttpCase(odoo.tests.HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        # Active skip payment for Mitchel Admin
        cls.partner = cls.env.ref("base.partner_admin")
        # VAT required by the module website_sale_vat_required
        cls.partner.vat = "US01234567891"
        cls.partner.with_context(**{"res_partner_search_mode": "customer"}).write(
            {"skip_website_checkout_payment": True}
        )
        cls.env["product.template"].create(
            {
                "name": "Test Product",
                "list_price": 100.0,
                "sale_ok": True,
                "is_published": True,
            }
        )
        cls.env["res.users"].search([("login", "=", "admin")]).partner_id.write(
            {
                "country_id": cls.env.ref("base.us").id,
                "street": "123 Test St",
                "city": "Test City",
                "zip": "12345",
                "email": "admin@example.com",
                "phone": "1234567890",
                "state_id": cls.env.ref("base.state_us_1").id,
            }
        )

    def test_checkout_skip_payment(self):
        website = self.env["website"].create({"name": "Test Website"})
        with patch(
            "odoo.addons.website_sale_checkout_skip_payment.models.website.request",
            new=Mock(),
        ) as request:
            request.session.uid = False
            self.assertFalse(website.checkout_skip_payment)

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour(
            "/",
            "website_sale_checkout_skip_payment",
            login="admin",
        )
