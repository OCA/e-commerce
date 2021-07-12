# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase


class UICase(HttpCase):
    """Test checkout flow with legal terms acceptance required.

    It would be nice to check also that the workflow isn't interrupted when the
    acceptance requirement views are disabled, but that's what upstream tests
    do, so we don't need to repeat them. We can assume that, if other tests in
    the same integrated environment don't fail because of lack of legal terms
    acceptance, then the flow is fine.
    """

    def setUp(self):
        """Ensure website lang is en_US."""
        super().setUp()
        website = self.env["website"].get_current_website()
        wiz = self.env["base.language.install"].create({"lang": "en_US"})
        wiz.website_ids = website
        wiz.lang_install()
        website.default_lang_id = self.env.ref("base.lang_en")
        # Activate Accept Terms & Conditions views, as explained in CONFIGURE.rst
        website.viewref(
            "website_sale_require_legal.address_require_legal"
        ).active = True
        website.viewref("website_sale.payment_sale_note").active = True

    def test_ui_website(self):
        """Test frontend tour."""
        tour = "website_sale_require_legal"
        self.browser_js(
            url_path="/shop",
            code="odoo.__DEBUG__.services['web_tour.tour'].run('%s')" % tour,
            ready="odoo.__DEBUG__.services['web_tour.tour'].tours.%s.ready" % tour,
        )
        # Assert that the sale order and partner have metadata logs
        order = self.env["sale.order"].search([("partner_id", "=", "Super Mario")])
        partner = order.partner_id
        self.assertTrue(
            order.message_ids.filtered(
                lambda one: "Website legal terms acceptance metadata" in one.body
            )
        )
        self.assertTrue(
            partner.message_ids.filtered(
                lambda one: "Website legal terms acceptance metadata" in one.body
            )
        )
