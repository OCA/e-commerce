# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import HttpCase, tagged

from odoo.addons.website_sale.tests.common import WebsiteSaleCommon


@tagged("post_install", "-at_install")
class TestWebsiteSaleComparisonHidePrice(HttpCase, WebsiteSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Compared product",
                "list_price": 4321.0,
                "is_published": True,
                "sale_ok": True,
            }
        )

    def _product_data(self):
        """/shop/compare/get_product_data as a logged-out visitor"""
        return self.make_jsonrpc_request(
            "/shop/compare/get_product_data", {"product_ids": [self.product.id]}
        )[0]

    def test_price_shown(self):
        data = self._product_data()
        self.assertTrue(data["price"])
        self.assertFalse(data["website_hide_price"])

    def test_price_hidden_for_partner(self):
        self.public_partner.website_show_price = False
        data = self._product_data()
        self.assertEqual(data["price"], 0.0)
        self.assertNotIn("strikethrough_price", data)
        self.assertTrue(data["website_hide_price"])

    def test_price_hidden_for_product(self):
        self.product.website_hide_price = True
        data = self._product_data()
        self.assertEqual(data["price"], 0.0)
        self.assertTrue(data["website_hide_price"])
