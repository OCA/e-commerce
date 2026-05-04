from unittest.mock import patch

from werkzeug.datastructures import OrderedMultiDict
from werkzeug.wrappers import Response

from odoo import Command
from odoo.http import request
from odoo.tests import HttpCase, tagged

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.website_sale.tests.common import MockRequest
from odoo.addons.website_sale_product_brand.controllers.main import (
    WebsiteSale as Website,
)


@tagged("post_install", "-at_install")
class TestWebsiteSaleFilterBrandHttpCase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Activate attribute's filter in /shop. By default it's disabled.
        website = cls.env["website"].with_context(website_id=1)
        website.viewref("website_sale.products_attributes").active = True
        # Activate filter category view
        cls.env.ref(
            "website_sale_product_brand.website_sale_filter_brand_products_brands"
        ).active = True
        cls.brand = cls.env["product.brand"].create({"name": "Tour Brand"})
        cls.env["product.template"].create(
            {
                "name": "Tour Product",
                "sale_ok": True,
                "website_published": True,
                "list_price": 10.0,
                "product_brand_id": cls.brand.id,
            }
        )
        login = "portal_brand"
        cls.portal_user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Portal Brand User",
                    "login": login,
                    "password": login,
                    "email": "portal_brand@example.com",
                    "group_ids": [Command.set([cls.env.ref("base.group_portal").id])],
                }
            )
        )

    def test_ui_website_admin(self):
        """Test frontend tour."""
        self.start_tour("/shop", "website_sale_filter_product_brand", login="admin")

    def test_ui_website_portal(self):
        """Test frontend tour."""
        self.start_tour(
            "/shop", "website_sale_filter_product_brand", login=self.portal_user.login
        )


class WebsiteSale(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].browse(1)
        cls.other_website = cls.env["website"].create(
            {
                "name": "Other Website",
                "company_id": cls.env.company.id,
            }
        )
        cls.WebsiteSaleController = Website()
        cls.public_user = cls.env.ref("base.public_user")
        cls.brand = cls.env["product.brand"].create({"name": "Test Brand"})
        cls.global_brand = cls.env["product.brand"].create(
            {"name": "Global Brand", "website_id": False}
        )
        cls.other_brand = cls.env["product.brand"].create(
            {
                "name": "Other Website Brand",
                "website_id": cls.other_website.id,
            }
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "sale_ok": True,
                "website_published": True,
                "product_brand_id": cls.brand.id,
            }
        )
        cls.env["product.template"].create(
            {
                "name": "Global Product",
                "sale_ok": True,
                "website_published": True,
                "product_brand_id": cls.global_brand.id,
            }
        )
        cls.env["product.template"].create(
            {
                "name": "Other Website Product",
                "sale_ok": True,
                "website_published": True,
                "product_brand_id": cls.other_brand.id,
            }
        )

    def test_brands_domain(self):
        brand_ids = self.brand
        products = self.env["product.template"].search([("sale_ok", "=", True)])
        brands_list = [str(brand_ids.id)]
        domain = [("product_brand_id", "=", brand_ids.id)]
        required_domain = [("product_brand_id", "in", [brand_ids.id])]
        required_domain2 = [("id", "=", 1), ("product_brand_id", "in", [brand_ids.id])]
        simple_domain = [("id", "=", 1)]
        res1 = []
        res2 = []
        res3 = []
        res4 = []

        with MockRequest(
            brand_ids.with_user(self.public_user).env,
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

    def test_build_brands_list_filters_other_websites(self):
        with MockRequest(
            self.env,
            website=self.website,
        ):
            brands = self.WebsiteSaleController._build_brands_list(
                [self.brand.id, self.global_brand.id, self.other_brand.id]
            )
        self.assertCountEqual(brands.ids, [self.brand.id, self.global_brand.id])

    def test_shop_controller_lines(self):
        class MockResponse(Response):
            def __init__(self, qcontext=None):
                super().__init__("Mock")
                self.qcontext = qcontext or {}

        with MockRequest(
            self.env,
            website=self.website,
        ):
            request.httprequest.args = OrderedMultiDict([("attribute_values", "1")])

            with patch(
                "odoo.addons.website_sale.controllers.main.WebsiteSale.shop"
            ) as mock_shop:
                mock_shop.return_value = MockResponse(qcontext={})
                res1 = self.WebsiteSaleController.shop(brand=str(self.brand.id))
                self.assertEqual(request.env.context.get("brand_ids"), [self.brand.id])
                self.assertEqual(res1.status_code, 200)

                class KeepMock:
                    args = {}

                keep_mock = KeepMock()
                mock_shop.return_value = MockResponse(
                    qcontext={
                        "attrib_values": [],
                        "products": self.product,
                        "keep": keep_mock,
                    }
                )
                with patch.object(
                    self.WebsiteSaleController, "_get_shop_domain_no_brands"
                ) as mock_domain:
                    mock_domain.return_value = [("id", "in", self.product.ids)]
                    res2 = self.WebsiteSaleController.shop(brand=str(self.brand.id))
                    self.assertEqual(keep_mock.args.get("brand"), [])
                    self.assertEqual(res2.status_code, 200)
                    return True

    def test_product_brands_controller(self):
        self.brand.website_published = True
        with MockRequest(self.env, website=self.website):
            with patch(
                "odoo.addons.website_sale_product_brand.controllers.main.request.render"
            ) as mock_render:
                mock_render.return_value = Response("Mocked Response")
                res = self.WebsiteSaleController.product_brands()
                self.assertEqual(res.status_code, 200)
                args, kwargs = mock_render.call_args
                self.assertNotIn("search", args[1])

                res = self.WebsiteSaleController.product_brands(search=self.brand.name)
                self.assertEqual(res.status_code, 200)
                args, kwargs = mock_render.call_args
                self.assertEqual(args[1]["search"], self.brand.name)

    def test_product_brands_controller_filters_other_websites(self):
        with MockRequest(self.env, website=self.website):
            with patch(
                "odoo.addons.website_sale_product_brand.controllers.main.request.render"
            ) as mock_render:
                mock_render.return_value = Response("Mocked Response")
                res = self.WebsiteSaleController.product_brands()
                self.assertEqual(res.status_code, 200)
                args, kwargs = mock_render.call_args
                brand_rec = args[1]["brand_rec"]
                self.assertIn(self.brand, brand_rec)
                self.assertIn(self.global_brand, brand_rec)
                self.assertNotIn(self.other_brand, brand_rec)
