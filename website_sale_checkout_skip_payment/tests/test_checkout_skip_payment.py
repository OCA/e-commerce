# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import Mock, patch

from odoo.tests.common import tagged

from odoo.addons.base.tests.common import HttpCaseWithUserDemo


@tagged("post_install", "-at_install")
class WebsiteSaleHttpCase(HttpCaseWithUserDemo):
    def setUp(self):
        super().setUp()
        # Active skip payment for Mitchel Admin
        self.partner = self.env.ref("base.partner_admin")
        self.partner.with_context(**{"res_partner_search_mode": "customer"}).write(
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
        user_demo = self.env.ref("base.user_demo")
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_checkout_skip_payment",
        )
        self.browser_js(
            url_path="/shop",
            code="%s.run('%s')" % tour,
            ready="%s.tours.%s.ready" % tour,
            login=user_demo.login,
            timeout=600,
        )
