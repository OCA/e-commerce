# Copyright 2026 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.http import Request, root
from odoo.tests import Form, HttpCase, new_test_user, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT

LOCKED_NOTICE = "Your addresses are managed by your company."
INCOMPLETE_NOTICE = "The address of your company is incomplete."
CONTACT_NOTICE = "Please complete your email and phone to continue with your order."


@tagged("post_install", "-at_install")
class TestWebsiteSaleAddressLock(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.product = cls.env["product.product"].create(
            {"name": "Croissant", "sale_ok": True, "website_published": True}
        )
        cls.address = {
            "street": "215 Vine St",
            "city": "Scranton",
            "zip": "18503",
            "state_id": cls.env.ref("base.state_us_39").id,
            "country_id": cls.env.ref("base.us").id,
            "phone": "+1 555 0100",
            "vat": "US01234567891",
        }
        cls.locked_user = cls._create_portal_user("locked_portal", lock=True)
        cls.unlocked_user = cls._create_portal_user("unlocked_portal", lock=False)
        cls.partner_manager = new_test_user(
            cls.env,
            login="address_lock_manager",
            groups="base.group_user,base.group_partner_manager",
        )

    @classmethod
    def _create_portal_user(cls, login, lock):
        company = cls.env["res.partner"].create(
            dict(cls.address, name=login, is_company=True, website_address_lock=lock)
        )
        return new_test_user(
            cls.env, login, "base.group_portal", parent_id=company.id, **cls.address
        )

    def _create_delivery(self, **values):
        return self.env["res.partner"].create(
            dict(
                self.address,
                name="Franchise Warehouse",
                type="delivery",
                parent_id=self.locked_user.parent_id.id,
                **values,
            )
        )

    def _start_checkout(self, user):
        order = self.env["sale.order"].create(
            {
                "partner_id": user.partner_id.id,
                "website_id": self.env.ref("website.default_website").id,
                "order_line": [Command.create({"product_id": self.product.id})],
            }
        )
        session = self.authenticate(user.login, user.login)
        session["sale_order_id"] = order.id
        root.session_store.save(session)
        return order

    def _post(self, url, **data):
        return self.url_open(url, data=dict(data, csrf_token=Request.csrf_token(self)))

    def _post_account(self, user, **values):
        partner = user.partner_id
        return self._post(
            "/my/account",
            **dict(
                {"name": partner.name, "email": partner.email, "phone": partner.phone},
                **values,
            ),
        )

    def test_lock_field_in_partner_form(self):
        company = self.env["res.partner"].create({"name": "New", "is_company": True})
        contact = self.env["res.partner"].create(
            {"name": "Contact", "parent_id": company.id}
        )
        single = self.env["res.partner"].create({"name": "Single Contact"})
        for partner in company | single:
            partner_form = Form(partner.with_user(self.partner_manager))
            partner_form.website_address_lock = True
            partner_form.save()
            self.assertTrue(partner.website_address_lock)
        contact_form = Form(contact.with_user(self.partner_manager))
        with self.assertRaises(AssertionError):
            contact_form.website_address_lock = True

    def test_checkout_locked_hides_edit_and_add(self):
        self._start_checkout(self.locked_user)
        response = self.url_open("/shop/checkout")
        self.assertTrue(response.url.endswith("/shop/checkout"))
        self.assertNotIn("js_edit_address", response.text)
        self.assertNotIn("o_wsale_add_address", response.text)
        self.assertIn(LOCKED_NOTICE, response.text)

    def test_locked_can_select_existing_address(self):
        delivery = self._create_delivery()
        order = self._start_checkout(self.locked_user)
        self._post("/shop/cart/update_address", partner_id=delivery.id, mode="shipping")
        self.assertEqual(order.partner_shipping_id, delivery)

    def test_address_route_closed(self):
        self._start_checkout(self.locked_user)
        contact = self.locked_user.partner_id
        for url in (
            "/shop/address",
            "/shop/address?mode=shipping&partner_id=%d" % contact.id,
        ):
            response = self.url_open(url, allow_redirects=False)
            self.assertEqual(response.status_code, 303)
            self.assertTrue(response.headers["Location"].endswith("/shop/checkout"))
        partner_count = self.env["res.partner"].search_count([])
        for partner_id in (-1, contact.id):
            response = self._post(
                "/shop/address",
                **dict(self.address, name="New", street="Changed St"),
                email="new@example.com",
                partner_id=partner_id,
                submitted=1,
            )
            self.assertEqual(response.status_code, 403)
        self.assertEqual(self.env["res.partner"].search_count([]), partner_count)
        self.assertEqual(contact.street, "215 Vine St")

    def test_incomplete_data_blocks_checkout(self):
        contact = self.locked_user.partner_id
        order = self._start_checkout(self.locked_user)
        contact.email = False
        response = self.url_open("/shop/checkout", allow_redirects=False)
        self.assertIn(
            "/my/account?redirect=/shop/checkout", response.headers["Location"]
        )
        contact.write({"email": "locked@example.com", "city": False})
        self.assertIn(INCOMPLETE_NOTICE, self.url_open("/shop/checkout").text)
        contact.city = "Scranton"
        order.partner_shipping_id = self._create_delivery(street=False)
        for url in ("/shop/checkout", "/shop/confirm_order"):
            response = self.url_open(url)
            self.assertTrue(response.url.endswith(url))
            self.assertIn(INCOMPLETE_NOTICE, response.text)
        self.assertEqual(order.state, "draft")

    def test_account_locked_keeps_address(self):
        contact = self.locked_user.partner_id
        self.authenticate(self.locked_user.login, self.locked_user.login)
        response = self.url_open("/my/account")
        self.assertNotIn('name="street"', response.text)
        self.assertIn(LOCKED_NOTICE, response.text)
        self.assertNotIn(CONTACT_NOTICE, response.text)
        response = self._post_account(
            self.locked_user, phone="+1 555 0199", street="Changed St", zipcode="1"
        )
        self.assertTrue(response.url.endswith("/my/home"))
        self.assertEqual(contact.phone, "+1 555 0199")
        self.assertEqual((contact.street, contact.zip), ("215 Vine St", "18503"))
        contact.email = False
        self.assertIn(CONTACT_NOTICE, self.url_open("/my/account").text)

    def test_unlocked_standard_behaviour(self):
        contact = self.unlocked_user.partner_id
        self._start_checkout(self.unlocked_user)
        response = self.url_open("/shop/checkout")
        self.assertIn("js_edit_address", response.text)
        self.assertIn("o_wsale_add_address", response.text)
        self.assertNotIn(LOCKED_NOTICE, response.text)
        response = self.url_open("/shop/address?mode=shipping")
        self.assertIn('name="street"', response.text)
        self.assertIn('name="street"', self.url_open("/my/account").text)
        response = self._post_account(
            self.unlocked_user,
            street="Changed St",
            city=contact.city,
            zipcode=contact.zip,
            state_id=contact.state_id.id,
            country_id=contact.country_id.id,
        )
        self.assertTrue(response.url.endswith("/my/home"))
        self.assertEqual(contact.street, "Changed St")
