# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form, HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleProductAccessory(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref("website.default_website")
        cls.main_product = cls.env["product.template"].create(
            {
                "name": "Test Main Product",
                "list_price": 100.0,
                "is_published": True,
                "website_published": True,
                "sale_ok": True,
            }
        )
        cls.accessory_product = cls.env["product.template"].create(
            {
                "name": "Test Accessory Product",
                "list_price": 25.0,
                "is_published": True,
                "website_published": True,
                "sale_ok": True,
            }
        )
        cls.unpublished_accessory = cls.env["product.template"].create(
            {
                "name": "Test Unpublished Accessory",
                "list_price": 15.0,
                "is_published": False,
                "website_published": False,
                "sale_ok": True,
            }
        )

    def _link_accessory_via_form(self, template, accessory_variant):
        """Mimic the user adding an accessory through the product form."""
        with Form(template) as form:
            form.accessory_product_ids.add(accessory_variant)

    def test_01_get_product_page_accessory_products_returns_published(self):
        self._link_accessory_via_form(
            self.main_product, self.accessory_product.product_variant_id
        )
        accessories = self.main_product._get_product_page_accessory_products()
        self.assertIn(self.accessory_product.product_variant_id, accessories)

    def test_02_unpublished_accessory_is_filtered_out(self):
        self.main_product.accessory_product_ids = [
            Command.link(self.unpublished_accessory.product_variant_id.id),
        ]
        accessories = self.main_product.with_user(
            self.env.ref("base.public_user")
        )._get_product_page_accessory_products()
        self.assertNotIn(self.unpublished_accessory.product_variant_id, accessories)

    def test_03_self_is_filtered_out(self):
        self.main_product.accessory_product_ids = [
            Command.link(self.main_product.product_variant_id.id),
        ]
        accessories = self.main_product._get_product_page_accessory_products()
        self.assertNotIn(self.main_product.product_variant_id, accessories)

    def test_04_product_page_renders_accessory_block(self):
        self._link_accessory_via_form(
            self.main_product, self.accessory_product.product_variant_id
        )
        response = self.url_open(self.main_product.website_url)
        self.assertEqual(response.status_code, 200)
        body = response.text
        self.assertIn("oe_structure_website_sale_product_accessory_products", body)
        self.assertIn(self.accessory_product.name, body)

    def test_05_product_page_no_block_when_no_accessory(self):
        response = self.url_open(self.main_product.website_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            "oe_structure_website_sale_product_accessory_products", response.text
        )
