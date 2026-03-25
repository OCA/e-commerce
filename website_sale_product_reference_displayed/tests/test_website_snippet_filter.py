# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.osv import expression
from odoo.tests import tagged

from odoo.addons.sale.tests.test_sale_product_attribute_value_config import (
    TestSaleProductAttributeValueCommon,
)
from odoo.addons.website.tools import MockRequest
from odoo.addons.website_sale.tests.common import WebsiteSaleCommon


@tagged("post_install", "-at_install")
class TestWebsiteSnippetFilter(WebsiteSaleCommon, TestSaleProductAttributeValueCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SnippetFilter = cls.env["website.snippet.filter"]
        cls.computer.write(
            {
                "company_id": False,
                "website_published": True,
            }
        )
        cls.accessory = cls.env["product.template"].create(
            {
                "name": "Accessory",
                "company_id": False,
                "website_published": True,
            }
        )
        cls.alternative = cls.env["product.template"].create(
            {
                "name": "Alternative",
                "company_id": False,
                "website_published": True,
            }
        )
        cls.computer.write(
            {
                "accessory_product_ids": [
                    Command.set(cls.accessory.product_variant_ids.ids)
                ],
                "alternative_product_ids": [Command.set(cls.alternative.ids)],
            }
        )

        cls.sold_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "website_id": cls.website.id,
                "order_line": [
                    Command.create({"product_id": cls.computer.product_variant_id.id}),
                    Command.create({"product_id": cls.accessory.product_variant_id.id}),
                ],
            }
        )
        cls.sold_order.action_confirm()

    def _domain(self):
        return expression.AND(
            [
                [("website_published", "=", True)],
                self.website.website_domain(),
                [("company_id", "in", [False, self.website.company_id.id])],
            ]
        )

    def test_latest_sold_sets_display_default_code(self):
        with MockRequest(self.env, website=self.website):
            result = self.SnippetFilter._get_products_latest_sold(
                website=self.website, limit=16, domain=self._domain()
            )
        self.assertTrue(result)
        self.assertTrue(result.env.context.get("display_default_code"))

    def test_latest_viewed_sets_display_default_code(self):
        with MockRequest(self.env, website=self.website):
            visitor = self.env["website.visitor"]._upsert_visitor(
                self.env.user.partner_id.id
            )
            self.env["website.track"].create(
                {
                    "visitor_id": visitor[0],
                    "product_id": self.accessory.product_variant_id.id,
                }
            )
            result = self.SnippetFilter._get_products_latest_viewed(
                website=self.website, limit=16, domain=self._domain()
            )
        self.assertTrue(result)
        self.assertTrue(result.env.context.get("display_default_code"))

    def test_recently_sold_with_sets_display_default_code(self):
        with MockRequest(self.env, website=self.website):
            result = self.SnippetFilter._get_products_recently_sold_with(
                website=self.website,
                limit=16,
                domain=self._domain(),
                product_template_id=self.computer.id,
            )
        self.assertTrue(result)
        self.assertTrue(result.env.context.get("display_default_code"))

    def test_accessories_sets_display_default_code(self):
        with MockRequest(self.env, website=self.website):
            result = self.SnippetFilter._get_products_accessories(
                website=self.website,
                limit=16,
                domain=self._domain(),
                product_template_id=self.computer.id,
            )
        self.assertTrue(result)
        self.assertTrue(result.env.context.get("display_default_code"))

    def test_alternative_products_sets_display_default_code(self):
        with MockRequest(self.env, website=self.website):
            result = self.SnippetFilter._get_products_alternative_products(
                website=self.website,
                limit=16,
                domain=self._domain(),
                product_template_id=self.computer.id,
            )
        self.assertTrue(result)
        self.assertTrue(result.env.context.get("display_default_code"))
