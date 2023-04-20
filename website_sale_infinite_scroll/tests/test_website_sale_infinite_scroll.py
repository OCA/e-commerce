from odoo.tests.common import HttpCase, SavepointCase, TransactionCase
from odoo.tools import base64_to_image

from odoo.addons.website.tools import MockRequest
from odoo.addons.website_sale_infinite_scroll.controllers.main import (
    WebsiteSaleInfinityScroll,
)


class TestWebsiteSaleHttpCase(HttpCase):
    def test_ui_website_portal(self):
        """Test frontend tour."""
        self.start_tour("/shop", "website_sale_infinite_scroll", login="portal")

    def test_check_page(self):
        req = self.url_open("/shop")
        self.assertEqual(req.status_code, 200)


class TestWebsiteSaleInfiniteScrollHttpCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestWebsiteSaleInfiniteScrollHttpCase, cls).setUpClass()
        cls.website = cls.env["website"].browse(1)
        cls.WebsiteSaleController = WebsiteSaleInfinityScroll()
        cls.public_user = cls.env.ref("base.public_user")

    def test_get_preload_url(self):
        self.assertTrue(self.website._default_preloader(), msg="Must be equal")
        with MockRequest(self.env, website=self.website.with_user(self.public_user)):
            result = (
                self.WebsiteSaleController.get_website_sale_infinite_scroll_preloader()
            )
            self.assertIn(
                result.location.split("=")[0],
                "/web/image/website/1/infinite_scroll_preloader?unique",
                msg="Must be equal",
            )

    def test_check_page(self):
        with MockRequest(self.env, website=self.website.with_user(self.public_user)):
            product_count = self.WebsiteSaleController._get_shop_ppg(20)
            self.assertEqual(product_count, 21, msg="Must be equal")


class TestWebsiteSaleInfiniteScroll(TransactionCase):
    def test_website_preloader(self):
        Website = self.env["website"]
        website = Website.create(
            {
                "name": "Test Website",
                "infinite_scroll_preloader": Website._default_preloader(),
            }
        )

        image = base64_to_image(website.infinite_scroll_preloader)
        self.assertEqual(image.format, "GIF")
