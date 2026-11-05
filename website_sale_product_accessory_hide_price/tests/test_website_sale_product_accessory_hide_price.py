# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleProductAccessoryHidePrice(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref("website.default_website")
        cls.accessory = cls.env["product.template"].create(
            {
                "name": "Test Hidden Price Accessory",
                "list_price": 4321.0,
                "is_published": True,
                "sale_ok": True,
            }
        )
        cls.main_product = cls.env["product.template"].create(
            {
                "name": "Test Main Product",
                "list_price": 100.0,
                "is_published": True,
                "sale_ok": True,
                "accessory_product_ids": [
                    Command.link(cls.accessory.product_variant_id.id)
                ],
            }
        )

    def _accessory_block(self):
        response = self.url_open(self.main_product.website_url)
        self.assertEqual(response.status_code, 200)
        body = response.text
        start = body.index("oe_structure_website_sale_product_accessory_products")
        return body[start:]

    def test_price_shown(self):
        self.assertIn("accessory_product_price_container", self._accessory_block())

    def test_price_hidden_for_partner(self):
        self.env.ref("base.public_partner").website_show_price = False
        block = self._accessory_block()
        self.assertIn(self.accessory.name, block)
        self.assertNotIn("accessory_product_price_container", block)

    def test_price_hidden_for_website(self):
        self.website.website_hide_price = True
        self.assertNotIn("accessory_product_price_container", self._accessory_block())

    def test_price_hidden_for_product(self):
        self.accessory.website_hide_price = True
        self.assertNotIn("accessory_product_price_container", self._accessory_block())
