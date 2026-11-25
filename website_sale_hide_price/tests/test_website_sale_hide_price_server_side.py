# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import AccessError
from odoo.tests import tagged

from odoo.addons.website_sale.tests.common import MockRequest, WebsiteSaleCommon

from ..controllers.main import _check_configurator_allowed


@tagged("post_install", "-at_install")
class TestWebsiteSaleHidePriceServerSide(WebsiteSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website.google_analytics_key = "G-TEST"
        cls.product = cls.env["product.product"].create(
            {
                "name": "Hidden price product",
                "list_price": 4321.0,
                "is_published": True,
                "sale_ok": True,
            }
        )
        cls.template = cls.product.product_tmpl_id

    def _public_env(self):
        return self.env(user=self.public_user)

    def test_combination_info_model_keeps_price(self):
        """Server-rendered templates hide the price themselves; zeroing it in
        the model would show 0.00 in the blocks that do not check it."""
        self.public_partner.website_show_price = False
        env = self._public_env()
        with MockRequest(env, website=self.website.with_env(env)):
            info = self.template.with_env(env)._get_combination_info()
        self.assertTrue(info["price"])

    def _markup_data(self):
        env = self._public_env()
        with MockRequest(env, website=self.website.with_env(env)):
            return self.product.with_env(env)._to_markup_data(self.website)

    def test_markup_data_price_shown(self):
        self.assertIn("price", self._markup_data()["offers"])

    def test_markup_data_price_hidden(self):
        self.public_partner.website_show_price = False
        self.assertNotIn("price", self._markup_data()["offers"])

    def _add_to_cart_allowed(self):
        env = self._public_env()
        with MockRequest(env, website=self.website.with_env(env)):
            return self.product.with_env(env)._is_add_to_cart_allowed()

    def test_add_to_cart_allowed(self):
        self.assertTrue(self._add_to_cart_allowed())

    def test_add_to_cart_blocked(self):
        self.public_partner.website_show_price = False
        self.assertFalse(self._add_to_cart_allowed())

    def _check_configurator(self):
        env = self._public_env()
        with MockRequest(env, website=self.website.with_env(env)):
            _check_configurator_allowed(self.template.id)

    def test_configurator_allowed(self):
        self._check_configurator()

    def test_configurator_blocked(self):
        self.public_partner.website_show_price = False
        with self.assertRaises(AccessError):
            self._check_configurator()

    def _show_quick_add(self):
        env = self._public_env()
        with MockRequest(env, website=self.website.with_env(env)):
            return self.product.with_env(env)._website_show_quick_add()

    def test_quick_add_shown(self):
        self.assertTrue(self._show_quick_add())

    def test_quick_add_hidden_price(self):
        """Not offered as a suggested accessory in the cart either"""
        self.template.website_hide_price = True
        self.assertFalse(self._show_quick_add())

    def _show_quick_add_template(self):
        env = self._public_env()
        with MockRequest(env, website=self.website.with_env(env)):
            return self.template.with_env(env)._website_show_quick_add()

    def test_shop_tile_quick_add_shown(self):
        self.assertTrue(self._show_quick_add_template())

    def test_shop_tile_quick_add_hidden_price(self):
        """The /shop tile button calls it on the template"""
        self.template.website_hide_price = True
        self.assertFalse(self._show_quick_add_template())

    def test_shop_tile_quick_add_hidden_for_partner(self):
        self.public_partner.website_show_price = False
        self.assertFalse(self._show_quick_add_template())
