# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleProductPublishDate(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        now = fields.Datetime.now()
        cls.test_product = (
            cls.env["product.template"]
            .sudo()
            .create(
                {
                    "name": "Test Product",
                    "list_price": 10.0,
                    "website_published": True,
                    "expected_publish_date": now - timedelta(days=1),
                    "expected_unpublish_date": now + timedelta(days=1),
                }
            )
        )
        cls.search_url = "/shop?search=Test+Product"

    def test_product_visible_in_valid_period(self):
        response = self.url_open(self.search_url)
        self.assertEqual(
            response.status_code, 200, "Shop page did not load successfully."
        )
        product_marker = b'content="Test Product"'
        self.assertIn(
            product_marker,
            response.content,
            "Product should be visible during its valid period.",
        )

    def test_product_not_visible_before_publish_date(self):
        self.test_product.write(
            {"expected_publish_date": fields.Datetime.now() + timedelta(days=1)}
        )
        response = self.url_open(self.search_url)
        self.assertEqual(
            response.status_code, 200, "Shop page did not load successfully."
        )
        product_marker = b'content="Test Product"'
        self.assertNotIn(
            product_marker,
            response.content,
            "Product should not be visible before its publish date.",
        )

    def test_product_not_visible_after_unpublish_date(self):
        self.test_product.write(
            {"expected_unpublish_date": fields.Datetime.now() - timedelta(days=1)}
        )
        response = self.url_open(self.search_url)
        self.assertEqual(
            response.status_code, 200, "Shop page did not load successfully."
        )
        product_marker = b'content="Test Product"'
        self.assertNotIn(
            product_marker,
            response.content,
            "Product should not be visible after its unpublish date.",
        )

    def test_product_visible_with_no_date_restrictions(self):
        self.test_product.write(
            {"expected_publish_date": False, "expected_unpublish_date": False}
        )
        response = self.url_open(self.search_url)
        self.assertEqual(
            response.status_code, 200, "Shop page did not load successfully."
        )
        product_marker = b'content="Test Product"'
        self.assertIn(
            product_marker,
            response.content,
            "Product should be visible when no date restrictions are set.",
        )
