# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import patch

from odoo.http import Response
from odoo.tests.common import tagged

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.website_sale.tests.common import MockRequest
from odoo.addons.website_sale_product_sort.controllers.main import (
    WebsiteSale as WebsiteSaleController,
)


class MockResponse(Response):
    def __init__(self, qcontext=None):
        super().__init__("Mock")
        self.qcontext = qcontext or {}


@tagged("post_install", "-at_install")
class TestWebsiteSaleProductSort(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref("website.default_website")
        cls.controller = WebsiteSaleController()

    def test_get_product_sort_criterias(self):
        sort_mapping = self.website._get_product_sort_criterias()

        self.assertEqual(
            [sort for sort, _label in sort_mapping],
            [
                "website_sequence asc",
                "create_date desc",
                "name asc",
                "name desc",
                "list_price asc",
                "list_price desc",
            ],
        )

    def test_settings_related_field_updates_website(self):
        settings = self.env["res.config.settings"].create(
            {"website_id": self.website.id}
        )

        settings.product_sort_criteria = "name desc"

        self.assertEqual(self.website.default_product_sort_criteria, "name desc")

    def test_get_search_order_uses_website_default(self):
        self.website.default_product_sort_criteria = "name desc"

        with MockRequest(self.env, website=self.website):
            order = self.controller._get_search_order({})

        self.assertEqual(order, "is_published desc, name desc, id desc")

    def test_get_search_order_delegates_to_super(self):
        with MockRequest(self.env, website=self.website):
            with patch(
                "odoo.addons.website_sale.controllers.main.WebsiteSale._get_search_order",
                return_value="super-order",
            ) as mock_super:
                order = self.controller._get_search_order({"order": "name asc"})

        mock_super.assert_called_once_with({"order": "name asc"})
        self.assertEqual(order, "super-order")

    def test_shop_sets_default_order_in_qcontext(self):
        self.website.default_product_sort_criteria = "list_price desc"

        with MockRequest(self.env, website=self.website):
            with patch(
                "odoo.addons.website_sale.controllers.main.WebsiteSale.shop",
                return_value=MockResponse(qcontext={}),
            ):
                response = self.controller.shop()

        self.assertEqual(response.qcontext["order"], "list_price desc")

    def test_shop_keeps_explicit_order_in_qcontext(self):
        self.website.default_product_sort_criteria = "list_price desc"

        with MockRequest(self.env, website=self.website):
            with patch(
                "odoo.addons.website_sale.controllers.main.WebsiteSale.shop",
                return_value=MockResponse(qcontext={}),
            ):
                response = self.controller.shop(order="name asc")

        self.assertEqual(response.qcontext["order"], "name asc")
