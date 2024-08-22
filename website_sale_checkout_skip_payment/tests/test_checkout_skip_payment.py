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
        self.start_tour("/shop", "website_sale_checkout_skip_payment", login="admin")
