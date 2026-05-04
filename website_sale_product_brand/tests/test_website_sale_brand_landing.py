# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleBrandLandingHttp(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Brand = cls.env["product.brand"]
        cls.Product = cls.env["product.template"]
        cls.other_website = cls.env["website"].create(
            {
                "name": "Other Website",
                "company_id": cls.env.company.id,
            }
        )
        cls.public_category = cls.env["product.public.category"].create(
            {"name": "Brand Landing"}
        )
        cls.brand_visible = cls.Brand.create(
            {
                "name": "Visible Brand",
                "website_published": True,
                "website_description": "<p>Visible brand content</p>",
                "website_footer": "<p>Visible brand footer</p>",
            }
        )
        cls.brand_hidden = cls.Brand.create(
            {
                "name": "Hidden Brand",
                "website_published": False,
            }
        )
        cls.brand_other_website = cls.Brand.create(
            {
                "name": "Other Website Brand",
                "website_published": True,
                "website_id": cls.other_website.id,
            }
        )

        cls.Product.create(
            {
                "name": "Brand Product",
                "type": "consu",
                "list_price": 15.0,
                "website_published": True,
                "sale_ok": True,
                "public_categ_ids": [Command.set([cls.public_category.id])],
                "product_brand_id": cls.brand_visible.id,
            }
        )
        cls.Product.create(
            {
                "name": "Other Product",
                "type": "consu",
                "list_price": 18.0,
                "website_published": True,
                "sale_ok": True,
                "public_categ_ids": [Command.set([cls.public_category.id])],
            }
        )

    def test_brand_route_returns_200_for_visible_brand(self):
        self.authenticate(None, None)
        response = self.url_open(self.brand_visible.website_url)
        self.assertEqual(response.status_code, 200)

    def test_brand_route_filters_products_to_brand(self):
        self.authenticate(None, None)
        response = self.url_open(self.brand_visible.website_url)
        self.assertIn("Brand Product", response.text)
        self.assertNotIn("Other Product", response.text)

    def test_non_visible_brand_returns_404(self):
        self.authenticate(None, None)
        response = self.url_open(self.brand_hidden.website_url)
        self.assertEqual(response.status_code, 404)

    def test_brand_from_other_website_returns_404(self):
        self.authenticate(None, None)
        response = self.url_open(self.brand_other_website.website_url)
        self.assertEqual(response.status_code, 404)

    def test_shop_brands_with_brand_param_uses_landing_page(self):
        self.authenticate(None, None)
        response = self.url_open(f"/shop/brands?brand={self.brand_visible.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Visible brand content", response.text)
        self.assertIn("Brand Product", response.text)
        self.assertIn("/shop/brand/", response.url)

    def test_shop_brands_unpublished_brand_does_not_redirect(self):
        self.authenticate(None, None)
        response = self.url_open(f"/shop/brands?brand={self.brand_hidden.id}")
        self.assertNotIn("/shop/brand/", response.url)

    def test_shop_brands_redirect_preserves_extra_query_params(self):
        self.authenticate(None, None)
        response = self.url_open(
            f"/shop/brands?brand={self.brand_visible.id}&search=test"
        )
        self.assertIn("/shop/brand/", response.url)
        self.assertIn("search=test", response.url)
