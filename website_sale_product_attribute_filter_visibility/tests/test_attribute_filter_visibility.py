# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class WebsiteSaleHttpCase(HttpCase):
    def setUp(self):
        super().setUp()
        Attribute = self.env["product.attribute"]
        AttributeValue = self.env["product.attribute.value"]
        ProductTemplate = self.env["product.template"]

        self.product_attribute_test_color = Attribute.create(
            {
                "website_published": True,
                "name": "Test Color",
                "create_variant": "no_variant",
                "visibility": "visible",
            }
        )
        self.product_attribute_value_color_red = AttributeValue.create(
            {
                "name": "Test Red",
                "attribute_id": self.product_attribute_test_color.id,
            }
        )
        self.product_attribute_value_color_green = AttributeValue.create(
            {
                "name": "Test Green",
                "attribute_id": self.product_attribute_test_color.id,
            }
        )
        self.product_attribute_value_color_blue = AttributeValue.create(
            {
                "name": "Test Blue",
                "attribute_id": self.product_attribute_test_color.id,
            }
        )

        self.product_attribute_test_size = Attribute.create(
            {
                "website_published": False,
                "name": "Test Size",
                "create_variant": "no_variant",
                "visibility": "visible",
            }
        )
        self.product_attribute_value_test_size_small = AttributeValue.create(
            {
                "name": "Size Small",
                "attribute_id": self.product_attribute_test_size.id,
            }
        )
        self.product_attribute_value_test_size_large = AttributeValue.create(
            {
                "name": "Size Large",
                "attribute_id": self.product_attribute_test_size.id,
            }
        )
        # do not rely on demo data at all
        self.product_template_1 = ProductTemplate.create(
            {
                "name": "Filter Visibility Test Product 1",
                "type": "consu",
                "list_price": 100.0,
                "is_published": True,
                "website_published": True,
                "sale_ok": True,
            }
        )
        self.product_template_1.write(
            {
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.product_attribute_test_color.id,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    [
                                        self.product_attribute_value_color_red.id,
                                        self.product_attribute_value_color_green.id,
                                    ],
                                )
                            ],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.product_attribute_test_size.id,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    [
                                        self.product_attribute_value_test_size_small.id,
                                        self.product_attribute_value_test_size_large.id,
                                    ],
                                )
                            ],
                        },
                    ),
                ]
            }
        )

        self.product_template_2 = ProductTemplate.create(
            {
                "name": "Filter Visibility Test Product 2",
                "type": "consu",
                "list_price": 120.0,
                "is_published": True,
                "website_published": True,
                "sale_ok": True,
            }
        )
        self.product_template_2.write(
            {
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.product_attribute_test_color.id,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    [
                                        self.product_attribute_value_color_blue.id,
                                    ],
                                )
                            ],
                        },
                    ),
                ]
            }
        )

        # Active attribute filters in /shop. By default it's disabled.
        self.env.ref("website_sale.products_attributes").active = True

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour(
            "/shop",
            "website_sale_product_attribute_filter_visibility",
            login="admin",
        )
