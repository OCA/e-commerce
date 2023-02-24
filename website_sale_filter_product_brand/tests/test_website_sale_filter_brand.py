from odoo.tests.common import HttpCase, SavepointCase

from odoo.addons.website.tools import MockRequest
from odoo.addons.website_sale_filter_product_brand.controllers.website_sale import (
    Website,
)


class TestWebsiteSaleFilterBrandHttpCase(HttpCase):
    def setUp(self):
        super().setUp()

        # Activate attribute's filter in /shop. By default it's disabled.
        website = self.env["website"].with_context(website_id=1)
        website.viewref("website_sale.products_attributes").active = True
        # Activate filter category view
        self.env.ref(
            "website_sale_filter_product_brand.website_sale_filter_brand_products_brands"
        ).active = True

    def test_ui_website_admin(self):
        """Test frontend tour."""
        self.start_tour("/shop", "website_sale_filter_product_brand", login="admin")

    def test_ui_website_portal(self):
        """Test frontend tour."""
        self.start_tour("/shop", "website_sale_filter_product_brand", login="portal")


class WebsiteSale(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(WebsiteSale, cls).setUpClass()
        cls.website = cls.env["website"].browse(1)
        cls.WebsiteSaleController = Website()
        cls.public_user = cls.env.ref("base.public_user")

    def test_brands_domain(self):
        brand_ids = (
            self.env["product.brand"]
            .search([])
            .filtered(lambda x: x.products_count > 0)
        )
        products = self.env["product.template"].search([("sale_ok", "=", True)])
        brands_list = [str(brand.id) for brand in brand_ids]
        domain = [("product_brand_id", "=", brand_ids[0].id)]
        required_domain = [("product_brand_id", "in", brand_ids.ids)]
        required_domain2 = [("id", "=", 1), ("product_brand_id", "in", brand_ids.ids)]
        simple_domain = [("id", "=", 1)]
        res1 = []
        res2 = []
        res3 = []
        res4 = []

        with MockRequest(
            brand_ids[0].with_user(self.public_user).env,
            website=self.website.with_user(self.public_user),
        ):
            res1 = self.WebsiteSaleController._update_domain(brands_list, domain)
            res2 = self.WebsiteSaleController._update_domain(brands_list, simple_domain)
            res3 = self.WebsiteSaleController._build_brands_list(brands_list)
            res4 = self.WebsiteSaleController._remove_extra_brands(
                brand_ids, products, True
            )
        self.assertEqual(res1, required_domain, "Must be the same")
        self.assertEqual(res2, required_domain2, "Must be the same")
        self.assertEqual(res3.ids, brand_ids.ids, "Must be the same")
        self.assertEqual(res4.ids, brand_ids.ids, "Must be the same")
