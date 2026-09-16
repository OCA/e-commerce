# Copyright 2026 Terrabit (https://www.terrabit.ro).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleBrandProductPage(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.public_category = cls.env["product.public.category"].create(
            {"name": "Brand Product Page"}
        )
        cls.brand = cls.env["product.brand"].create(
            {
                "name": "Product Page Brand",
                "website_published": True,
                "website_description": "<p>Brand description on product page</p>",
            }
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "Branded Product",
                "type": "consu",
                "list_price": 20.0,
                "website_published": True,
                "sale_ok": True,
                "public_categ_ids": [Command.set([cls.public_category.id])],
                "product_brand_id": cls.brand.id,
            }
        )

    def test_brand_description_hidden_by_default(self):
        self.authenticate(None, None)
        response = self.url_open(self.product.website_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Brand description on product page", response.text)

    def test_brand_description_shown_when_enabled(self):
        self.brand.show_description_on_product_page = True
        self.authenticate(None, None)
        response = self.url_open(self.product.website_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Brand description on product page", response.text)

    def test_brand_description_not_shown_when_empty(self):
        self.brand.write(
            {
                "show_description_on_product_page": True,
                "website_description": False,
            }
        )
        self.authenticate(None, None)
        response = self.url_open(self.product.website_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("o_product_brand_description", response.text)
