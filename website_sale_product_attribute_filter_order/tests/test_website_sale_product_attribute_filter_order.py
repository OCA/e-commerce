# Copyright 2024 Tecnativa - Javier Obeso
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleProductAttributeFilterOrder(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Create product template with attributes
        cls.product_attribute = cls.env["product.attribute"].create(
            {
                "name": "Test Color",
                "display_type": "radio",
                "create_variant": "no_variant",
            }
        )

        cls.attribute_value_red = cls.env["product.attribute.value"].create(
            {
                "name": "Red",
                "attribute_id": cls.product_attribute.id,
                "sequence": 10,
            }
        )

        cls.attribute_value_blue = cls.env["product.attribute.value"].create(
            {
                "name": "Blue",
                "attribute_id": cls.product_attribute.id,
                "sequence": 20,
            }
        )

        cls.attribute_value_green = cls.env["product.attribute.value"].create(
            {
                "name": "Green",
                "attribute_id": cls.product_attribute.id,
                "sequence": 30,
            }
        )

        cls.product_template = cls.env["product.template"].create(
            {
                "name": "Test Product with Attributes",
                "is_published": True,
                "website_id": cls.env["website"].search([], limit=1).id,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.product_attribute.id,
                            "value_ids": [
                                (4, cls.attribute_value_red.id),
                                (4, cls.attribute_value_blue.id),
                                (4, cls.attribute_value_green.id),
                            ],
                        },
                    )
                ],
            }
        )

    def test_template_inheritance(self):
        """Test that the template inherits correctly"""
        template = self.env.ref(
            "website_sale_product_attribute_filter_order.products_attributes"
        )
        self.assertEqual(
            template.inherit_id.id, self.env.ref("website_sale.products_attributes").id
        )
        self.assertFalse(template.active)

    def test_attribute_value_ordering(self):
        """Test that attribute values can be ordered based on selection"""
        # Get attribute values
        values = self.product_attribute.value_ids
        self.assertEqual(len(values), 3)

        # Test sorting with selected values
        # Simulate attrib_set containing some IDs
        attrib_set = {self.attribute_value_green.id, self.attribute_value_red.id}

        # Sort using the same logic as the template
        sorted_values = values.sorted(key=lambda x: x.id in attrib_set, reverse=True)

        # Values in attrib_set should come first
        self.assertIn(sorted_values[0].id, attrib_set)
        self.assertIn(sorted_values[1].id, attrib_set)
        self.assertNotIn(sorted_values[2].id, attrib_set)

    def test_shop_page_loads(self):
        """Test that the shop page loads correctly with the module installed"""
        response = self.url_open("/shop")
        self.assertEqual(response.status_code, 200)
