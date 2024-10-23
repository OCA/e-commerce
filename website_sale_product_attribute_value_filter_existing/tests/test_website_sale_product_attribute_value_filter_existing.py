# Copyright 2019 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.tests.common import HttpCase, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class WebsiteSaleHttpCase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        # Models
        ProductAttribute = cls.env["product.attribute"]
        ProductAttributeValue = cls.env["product.attribute.value"]
        ProductAttributeLine = cls.env["product.template.attribute.line"]
        cls.product_attribute = ProductAttribute.create(
            {
                "name": "Test Special Color",
                "display_type": "color",
                "create_variant": "no_variant",
            }
        )
        cls.product_attribute_value_red = ProductAttributeValue.create(
            {
                "name": "Test red",
                "attribute_id": cls.product_attribute.id,
                "html_color": "#ff0000",
            }
        )
        cls.product_attribute_value_green = ProductAttributeValue.create(
            {
                "name": "Test green",
                "attribute_id": cls.product_attribute.id,
                "html_color": "#1dff00",
            }
        )
        cls.product_attribute_value_blue = ProductAttributeValue.create(
            {
                "name": "Test blue",
                "attribute_id": cls.product_attribute.id,
                "html_color": "#0000ff",
            }
        )
        cls.product_attribute_value_yellow = ProductAttributeValue.create(
            {
                "name": "Test yellow",
                "attribute_id": cls.product_attribute.id,
                "html_color": "#FDEA01",
            }
        )
        cls.product_template = cls.env.ref("product.product_product_4_product_template")
        cls.product_attribute_line = ProductAttributeLine.create(
            {
                "product_tmpl_id": cls.product_template.id,
                "attribute_id": cls.product_attribute.id,
                "value_ids": [
                    (
                        6,
                        0,
                        [
                            cls.product_attribute_value_red.id,
                            cls.product_attribute_value_green.id,
                        ],
                    )
                ],
            }
        )
        cls.product_template.write(
            {"attribute_line_ids": [(4, cls.product_attribute_line.id)]}
        )
        cls.product_template_11 = cls.env.ref(
            "product.product_product_11_product_template"
        )
        cls.product_attribute_line_11 = ProductAttributeLine.create(
            {
                "product_tmpl_id": cls.product_template_11.id,
                "attribute_id": cls.product_attribute.id,
                "value_ids": [
                    (
                        6,
                        0,
                        [
                            cls.product_attribute_value_red.id,
                            cls.product_attribute_value_blue.id,
                        ],
                    )
                ],
            }
        )
        cls.product_template_11.write(
            {"attribute_line_ids": [(4, cls.product_attribute_line_11.id)]}
        )
        # Active attribute's filter in /shop. By default it's disabled.
        cls.env.ref("website_sale.products_attributes").active = True

    def test_ui_website(self):
        # This test ensures that unused attributes are not visible in the filter panel.
        self.start_tour(
            "/",
            "website_sale_product_attribute_value_filter_existing",
            login="admin",
            # deplay step here to ensure the tests pass
            step_delay=100,
        )

    def test_ui_website_search_desk(self):
        # This test ensures that attributes not used in the products displayed after a
        # search are not visible in the filter panel.
        self.start_tour(
            "/",
            "website_sale_product_attribute_value_filter_existing_search_desk",
            login="admin",
            # deplay step here to ensure the tests pass
            step_delay=100,
        )
