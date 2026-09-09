# Copyright 2019 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from lxml import html

from odoo.tests.common import HttpCase, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT

# radio and multi attributes render differently above 20 values
LARGE_ATTRIBUTE_SIZE = 25


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
        # Demo data not available in v19, create test products
        ProductTemplate = cls.env["product.template"]
        cls.product_template = ProductTemplate.create(
            {
                "name": "Test Product 1",
                "sale_ok": True,
                "is_published": True,
                "list_price": 100.0,
            }
        )
        cls.product_template_2 = ProductTemplate.create(
            {
                "name": "Test Product 2",
                "sale_ok": True,
                "is_published": True,
                "list_price": 200.0,
            }
        )

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
        cls.product_attribute_line_2 = ProductAttributeLine.create(
            {
                "product_tmpl_id": cls.product_template_2.id,
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
        cls.product_template_2.write(
            {"attribute_line_ids": [(4, cls.product_attribute_line_2.id)]}
        )
        # One attribute per display type, product 1 uses the first value,
        # product 2 the second one, the remaining values are never used.
        cls.attribute_radio = cls._create_attribute("radio")
        cls.attribute_radio_large = cls._create_attribute("radio", LARGE_ATTRIBUTE_SIZE)
        cls.attribute_multi = cls._create_attribute("multi")
        cls.attribute_multi_large = cls._create_attribute("multi", LARGE_ATTRIBUTE_SIZE)
        cls.attribute_select = cls._create_attribute("select")
        cls.attribute_image = cls._create_attribute("image")
        cls.attribute_pills = cls._create_attribute("pills")
        # Active attribute's filter in /shop. By default it's disabled.
        cls.env.ref("website_sale.products_attributes").active = True
        cls.env.ref("website_sale.search").active = True
        website = cls.env["website"].get_current_website()
        cls.env["website"].with_context(website_id=website.id).viewref(
            "website_sale.products_attributes"
        ).active = True
        cls.env["website"].with_context(website_id=website.id).viewref(
            "website_sale.search"
        ).active = True

    @classmethod
    def _create_attribute(cls, display_type, size=3):
        attribute = cls.env["product.attribute"].create(
            {
                "name": f"Test {display_type} {size}",
                "display_type": display_type,
                "create_variant": "no_variant",
                "value_ids": [
                    (0, 0, {"name": f"Test {display_type} value {i}"})
                    for i in range(size)
                ],
            }
        )
        for product, value in (
            (cls.product_template, attribute.value_ids[0]),
            (cls.product_template_2, attribute.value_ids[1]),
        ):
            product.attribute_line_ids = [
                (0, 0, {"attribute_id": attribute.id, "value_ids": [(4, value.id)]})
            ]
        return attribute

    def _assert_only_used_values(self, attribute):
        page = html.fromstring(self.url_open("/shop").content)
        # Values render as checkbox inputs, or as options for select attributes
        values = page.xpath(
            f"""
            //form[contains(concat(" ", @class, " "), " js_attributes ")]
            //*[self::input or self::option]
            [starts-with(@value, "{attribute.id}-")]/@value
            """
        )
        rendered = {int(value.split("-")[1]) for value in values}
        self.assertEqual(rendered, set(attribute.value_ids[:2].ids))

    def test_radio(self):
        self._assert_only_used_values(self.attribute_radio)

    def test_radio_large(self):
        self._assert_only_used_values(self.attribute_radio_large)

    def test_multi(self):
        self._assert_only_used_values(self.attribute_multi)

    def test_multi_large(self):
        self._assert_only_used_values(self.attribute_multi_large)

    def test_select(self):
        self._assert_only_used_values(self.attribute_select)

    def test_image(self):
        self._assert_only_used_values(self.attribute_image)

    def test_pills(self):
        self._assert_only_used_values(self.attribute_pills)

    def test_ui_website(self):
        # This test ensures that unused attributes are not visible in the filter panel.
        self.start_tour(
            "/",
            "website_sale_product_attribute_value_filter_existing",
            login="admin",
        )

    def test_ui_website_search_desk(self):
        # This test ensures that attributes not used in the products displayed after a
        # search are not visible in the filter panel.
        self.start_tour(
            "/",
            "website_sale_product_attribute_value_filter_existing_search_desk",
            login="admin",
        )
