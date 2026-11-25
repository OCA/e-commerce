# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests import HttpCase, tagged

from odoo.addons.website_sale.tests.common import WebsiteSaleCommon


@tagged("post_install", "-at_install")
class TestWebsiteSaleHidePriceJson(HttpCase, WebsiteSaleCommon):
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

    def _combination_info(self):
        """/website_sale/get_combination_info as a logged-out visitor"""
        return self.make_jsonrpc_request(
            "/website_sale/get_combination_info",
            {
                "product_template_id": self.template.id,
                "product_id": False,
                "combination": [],
                "add_qty": 1,
            },
        )

    def test_price_shown(self):
        info = self._combination_info()
        self.assertTrue(info["price"])
        self.assertTrue(info["product_tracking_info"]["price"])
        self.assertFalse(info["website_hide_price"])

    def test_price_hidden_for_partner(self):
        self.public_partner.website_show_price = False
        info = self._combination_info()
        self.assertEqual(info["price"], 0.0)
        self.assertEqual(info["list_price"], 0.0)
        self.assertEqual(info["product_tracking_info"]["price"], 0.0)
        self.assertTrue(info["website_hide_price"])

    def test_price_hidden_for_website(self):
        self.website.website_hide_price = True
        self.assertEqual(self._combination_info()["price"], 0.0)

    def test_price_hidden_for_product(self):
        self.template.website_hide_price = True
        self.assertEqual(self._combination_info()["price"], 0.0)

    def test_configurator_optional_product_price_hidden(self):
        """A visible product can have an optional product with a hidden price"""
        optional = self.env["product.product"].create(
            {
                "name": "Hidden price optional product",
                "list_price": 1234.0,
                "is_published": True,
                "sale_ok": True,
                "website_hide_price": True,
            }
        )
        self.template.optional_product_ids = optional.product_tmpl_id
        values = self.make_jsonrpc_request(
            "/website_sale/product_configurator/get_values",
            {
                "product_template_id": self.template.id,
                "quantity": 1,
                "so_date": fields.Datetime.now().isoformat(),
            },
        )
        self.assertTrue(values["products"][0]["price"])
        optional_values = [
            p
            for p in values["optional_products"]
            if p["product_tmpl_id"] == optional.product_tmpl_id.id
        ]
        self.assertTrue(optional_values)
        self.assertEqual(optional_values[0]["price"], 0.0)
