# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import HttpCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class WebsiteSaleAttributeFilterCategoryHttpCase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        # Models
        AttributeCategory = cls.env["product.attribute.category"]
        ProductAttribute = cls.env["product.attribute"]
        ProductAttributeValue = cls.env["product.attribute.value"]
        ProductAttributeLine = cls.env["product.template.attribute.line"]
        cls.attribute_category = AttributeCategory.create(
            {"name": "Test category", "website_folded": False}
        )
        cls.product_attribute = ProductAttribute.create(
            {
                "name": "Test",
                "create_variant": "no_variant",
                "category_id": cls.attribute_category.id,
            }
        )
        cls.product_attribute_value_test_1 = ProductAttributeValue.create(
            {"name": "Test v1", "attribute_id": cls.product_attribute.id}
        )
        cls.product_attribute_value_test_2 = ProductAttributeValue.create(
            {"name": "Test v2", "attribute_id": cls.product_attribute.id}
        )
        cls.product_template = cls.env.ref("product.product_product_4_product_template")
        cls.product_attribute_line = ProductAttributeLine.create(
            {
                "product_tmpl_id": cls.product_template.id,
                "attribute_id": cls.product_attribute.id,
                "value_ids": [
                    Command.set(
                        [
                            cls.product_attribute_value_test_1.id,
                            cls.product_attribute_value_test_2.id,
                        ],
                    )
                ],
            }
        )
        cls.product_template.write(
            {
                "attribute_line_ids": [(4, cls.product_attribute_line.id)],
                "is_published": True,
            }
        )
        # Active filter in /shop.
        cls.env.ref("website_sale.products_attributes").active = True
        cls.env.ref(
            "website_sale_product_attribute_filter_category.products_attributes_categories"
        ).active = True

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour(
            "/shop",
            "website_sale_product_attribute_filter_category",
            login="admin",
        )
