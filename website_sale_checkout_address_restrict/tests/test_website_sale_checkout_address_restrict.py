# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.addons.website.tools import MockRequest

from ..controllers.main import WebsiteSale


class TestWebsiteSaleCheckoutAddressRestrict(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Param = cls.env["ir.config_parameter"].sudo()
        cls.Partner = cls.env["res.partner"]
        cls.WebsiteSale = WebsiteSale()
        cls.website = cls.env.ref("website.default_website")
        cls.product = cls.env.ref("product.product_product_4")
        cls.demo_user = cls.env.ref("base.demo_user0")
        cls.partner_demo = cls.demo_user.partner_id

        # Create two child addresses with partner_demo as parent
        cls.child1 = cls.Partner.create(
            {
                "name": "Acme Ship 1",
                "parent_id": cls.partner_demo.id,
                "type": "delivery",
                "email": "child1@example.com",
                "website_id": cls.website.id,
            }
        )
        cls.child2 = cls.Partner.create(
            {
                "name": "Acme Ship 2",
                "parent_id": cls.partner_demo.id,
                "type": "other",
                "email": "child2@example.com",
                "website_id": cls.website.id,
            }
        )

        cls.child1_portal_user = cls._create_portal_user(cls.child1)
        cls.child1_portal_user.action_grant_access()
        cls.child1_portal_user = cls.env["res.users"].search(
            [("email", "=", cls.child1.email)]
        )

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_demo.id,
                "website_id": cls.website.id,
            }
        )

    @classmethod
    def _create_portal_user(cls, partner):
        """Return a portal wizard user from a partner."""
        portal_wizard = (
            cls.env["portal.wizard"].with_context(active_ids=[partner.id]).create({})
        )
        return portal_wizard.user_ids

    def test_checkout_values_parent_sees_all_addresses(self):
        """Parent contact sees all addresses when filter is disabled."""
        self.Param.set_param("website_sale.filter_child_shipping", "False")
        with MockRequest(self.env, website=self.website.with_user(self.demo_user)):
            vals = self.WebsiteSale.checkout_values()
        ids = vals["shippings"].mapped("id")
        self.assertIn(self.partner_demo.id, ids)
        self.assertIn(self.child1.id, ids)
        self.assertIn(self.child2.id, ids)

    def test_checkout_values_child_sees_own_address_only(self):
        """Child contact sees only its own address when filter is enabled."""
        self.Param.set_param("website_sale.filter_child_shipping", "True")
        self.order.partner_id = self.child1
        with MockRequest(
            self.order.with_user(self.child1_portal_user).env,
            website=self.website.with_user(self.child1_portal_user),
        ):
            vals = self.WebsiteSale.checkout_values()
        ids = vals["shippings"].mapped("id")
        self.assertIn(self.child1.id, ids)
        self.assertNotIn(self.partner_demo.id, ids)
        self.assertNotIn(self.child2.id, ids)

    def test_express_disabled_flag(self):
        """Test _express_disabled() reflects config parameter."""
        self.Param.set_param("website_sale.disable_express_checkout", "False")
        with MockRequest(self.env, website=self.website):
            self.assertFalse(self.WebsiteSale._express_disabled())

        self.Param.set_param("website_sale.disable_express_checkout", "True")
        with MockRequest(self.env, website=self.website):
            self.assertTrue(self.WebsiteSale._express_disabled())

    def test_cart_update_and_checkout_strip_express(self):
        """Test express checkout is stripped when disabled."""
        self.Param.set_param("website_sale.disable_express_checkout", "True")
        kw = {"express": "1"}
        with MockRequest(self.env, website=self.website.with_user(self.demo_user)):
            res = self.WebsiteSale.cart_update(
                product_id=self.product.id, add_qty=1, set_qty=0, **kw
            )
        self.assertIn("/shop/cart", res.location)
        self.assertNotIn("express=1", res.location)

        post = {"express": "1"}
        with MockRequest(
            self.order.with_user(self.demo_user).env,
            website=self.website.with_user(self.demo_user),
        ):
            res = self.WebsiteSale.checkout(**post)
        self.assertNotIn("/shop/confirm_oder", res.location)
