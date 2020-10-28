# Copyright 2019 Tecnativa - Sergio Teruel
# Copyright 2020 Iván Todorovich
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import odoo.tests


@odoo.tests.tagged("-at_install", "post_install")
class WebsiteSaleProductAttributeFilterCategoryHttpCase(odoo.tests.HttpCase):
    def setUp(self):
        super().setUp()
        # Models
        AttributeCategory = self.env["product.attribute.category"]
        ProductAttribute = self.env["product.attribute"]
        ProductAttributeValue = self.env["product.attribute.value"]
        ProductAttributeLine = self.env["product.template.attribute.line"]
        self.attribute_category = AttributeCategory.create(
            {"name": "Test category", "website_folded": False}
        )
        self.product_attribute = ProductAttribute.create(
            {
                "name": "Test",
                "create_variant": "no_variant",
                "category_id": self.attribute_category.id,
            }
        )
        self.product_attribute_value_test_1 = ProductAttributeValue.create(
            {"name": "Test v1", "attribute_id": self.product_attribute.id}
        )
        self.product_attribute_value_test_2 = ProductAttributeValue.create(
            {"name": "Test v2", "attribute_id": self.product_attribute.id}
        )
        self.product_template = self.env.ref(
            "product.product_product_4_product_template"
        )
        self.product_attribute_line = ProductAttributeLine.create(
            {
                "product_tmpl_id": self.product_template.id,
                "attribute_id": self.product_attribute.id,
                "value_ids": [
                    (
                        6,
                        0,
                        [
                            self.product_attribute_value_test_1.id,
                            self.product_attribute_value_test_2.id,
                        ],
                    )
                ],
            }
        )
        self.product_template.write(
            {
                "attribute_line_ids": [(4, self.product_attribute_line.id)],
                "is_published": True,
            }
        )
        # Activate attribute's filter in /shop. By default it's disabled.
        website = self.env["website"].with_context(website_id=1)
        website.viewref("website_sale.products_attributes").active = True
        # Activate filter category view
        module_name = "website_sale_product_attribute_filter_category"
        self.env.ref("%s.products_attributes" % module_name).active = True

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour("/shop", "website_sale_product_attribute_filter_category")
