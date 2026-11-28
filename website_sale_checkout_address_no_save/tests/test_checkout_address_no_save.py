# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import odoo.http
from odoo import Command
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
            "website_sale_checkout_address_no_save.archive_address_dropshipping"
        ).active = True
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
                "website_sale_checkout_address_no_save_no_pay",
                stepDelay=100,
                login="super_mario",
            )
            partner = self.user.partner_id
            self.assertTrue(partner.child_ids.active)
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
                "website_sale_checkout_address_no_save",
                stepDelay=100,
                login="super_mario",
            )
            # Assert that the partner have metadata logs
            partner = self.user.partner_id
            self.assertFalse(partner.child_ids.active)


@tagged("post_install", "-at_install")
class TestMainAddressNotArchived(HttpCase):
    def setUp(self):
        super().setUp()
        website = self.env["website"].get_current_website()
        website.viewref(
            "website_sale_checkout_address_no_save.archive_address_dropshipping"
        ).active = True
        self.user = new_test_user(
            self.env,
            login="portal_no_save",
            groups="base.group_portal",
            password="portal_no_save",
        )
        self.partner = self.user.partner_id
        product = self.env["product.product"].create(
            {"name": "Test product", "list_price": 10.0, "website_published": True}
        )
        self.order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "website_id": website.id,
                "order_line": [Command.create({"product_id": product.id})],
            }
        )

    def _url_open_with_session(self, url, **session_values):
        session = self.authenticate("portal_no_save", "portal_no_save")
        session.update(session_values)
        odoo.http.root.session_store.save(session)
        response = self.url_open(url)
        self.env.invalidate_all()
        return response

    def _open_payment_status(self):
        return self._url_open_with_session(
            "/payment/status",
            sale_last_order_id=self.order.id,
            archive_address=True,
        )

    def test_main_address_not_archived_after_checkout(self):
        response = self._open_payment_status()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.partner.active)

    def test_one_off_delivery_address_archived_after_checkout(self):
        child = self.env["res.partner"].create(
            {"name": "One-off delivery", "type": "other", "parent_id": self.partner.id}
        )
        self.order.partner_shipping_id = child
        self._open_payment_status()
        self.assertFalse(child.active)
        self.assertTrue(self.partner.active)

    def test_archive_checkbox_hidden_on_main_address_form(self):
        response = self._url_open_with_session(
            f"/shop/address?partner_id={self.partner.id}&address_type=delivery",
            sale_order_id=self.order.id,
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('name="archive_address"', response.text)
        response = self.url_open("/shop/address?address_type=delivery")
        self.assertIn('name="archive_address"', response.text)
