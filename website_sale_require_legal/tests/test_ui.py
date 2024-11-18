# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import new_test_user, tagged
from odoo.tests.common import HttpCase


@tagged("post_install", "-at_install")
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
        en_US = (
            self.env["res.lang"]
            .with_context(active_test=False)
            .search([("code", "=", "en_US")])
        )
        wiz = self.env["base.language.install"].create({"lang_ids": en_US.ids})
        self.env.flush_all()
        wiz.website_ids = website
        wiz.lang_install()
        website.default_lang_id = self.env.ref("base.lang_en")
        # Activate Accept Terms & Conditions views, as explained in CONFIGURE.rst
        website.viewref(
            "website_sale_require_legal.address_require_legal"
        ).active = True
        website.viewref("website_sale.accept_terms_and_conditions").active = True
        self.user = new_test_user(
            self.env,
            login="super_mario",
            groups="base.group_portal",
            password="super_mario",
            name="Super Mario",
        )

    def test_ui_website(self):
        """Test frontend tour."""
        if self.env["ir.module.module"]._get("payment_custom").state != "installed":
            self.start_tour(
                "/shop",
                "website_sale_require_legal",
                stepDelay=100,
                login="super_mario",
            )
        else:
            transfer_provider = self.env.ref("payment.payment_provider_transfer")
            transfer_provider.write(
                {
                    "state": "enabled",
                    "is_published": True,
                }
            )
            transfer_provider._transfer_ensure_pending_msg_is_set()
            self.start_tour(
                "/shop",
                "website_sale_require_legal_with_payment",
                stepDelay=100,
                login="super_mario",
            )
            order = self.env["sale.order"].search(
                [
                    ("partner_id", "ilike", "super_mario"),
                    ("website_id", "!=", "False"),
                ]
            )
            # Assert that the sale order have metadata logs
            self.assertTrue(
                order.message_ids.filtered(
                    lambda one: "Website legal terms acceptance metadata" in one.body
                )
            )
        # Assert that the partner have metadata logs
        partner = self.user.partner_id
        self.assertTrue(
            partner.message_ids.filtered(
                lambda one: "Website legal terms acceptance metadata" in one.body
            )
        )
