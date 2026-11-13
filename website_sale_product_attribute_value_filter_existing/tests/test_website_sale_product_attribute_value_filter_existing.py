# Copyright 2019 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from lxml import html

from odoo.tests.common import HttpCase, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CREATE_CONTEXT

# radio and multi attributes render differently above 20 values
LARGE_ATTRIBUTE_SIZE = 25


@tagged("post_install", "-at_install")
class WebsiteSaleHttpCase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CREATE_CONTEXT))
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
        # Demo data not available in v19, create test products.
        # Since 20.0 the shop search also looks into the attribute value names
        # (`attribute_line_ids.value_ids.name`), so the product names must not
        # share any word with them, or searching one product finds them all.
        ProductTemplate = cls.env["product.template"]
        cls.product_template = ProductTemplate.create(
            {
                "name": "Alpha",
                "sale_ok": True,
                "is_published": True,
                "list_price": 100.0,
            }
        )
        cls.product_template_2 = ProductTemplate.create(
            {
                "name": "Beta",
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
        # Not `product_attribute`: that one is the attribute filtered on
        cls.attribute_color = cls._create_attribute("color")
        # Active attribute's filter in /shop. By default it's disabled.
        cls.env.ref("website_sale.products_attributes").active = True
        cls.env.ref("website_sale.search").active = True
        # `get_current_website` was removed in 20.0, there is no request here
        website = cls.env.ref("base.default_website")
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

    def _rendered_values(self, attribute, url="/shop"):
        """Return the IDs of `attribute` values offered in the filter panel at `url`."""
        page = html.fromstring(self.url_open(url).content)
        # Values render as checkbox inputs, or as options for select attributes.
        # Stay on the attribute inputs: the same form also holds the tag and
        # price filters, and the range attributes of 20.0.
        values = page.xpath(
            """
            //form[contains(concat(" ", @class, " "), " js_attributes ")]
            //*[self::input[@name="attribute_value"]
                or self::option[parent::select[@name="attribute_value"]]]/@value
            """
        )
        # Since 20.0 the value is "<attribute slug>/<attribute value slug>"
        unslug = self.env["ir.http"]._unslug
        rendered = set()
        for value in values:
            attribute_slug, _, value_slug = value.partition("/")
            if not value_slug or unslug(attribute_slug)[1] != attribute.id:
                continue
            if value_id := unslug(value_slug)[1]:
                rendered.add(value_id)
        return rendered

    def _assert_only_used_values(self, attribute):
        self.assertEqual(
            self._rendered_values(attribute), set(attribute.value_ids[:2].ids)
        )

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

    def test_color(self):
        self._assert_only_used_values(self.attribute_color)

    def test_choosing_a_value_narrows_the_other_attributes(self):
        """Choosing a value also narrows down the other attributes.

        Since 20.0 Odoo drops on its own the values that no displayed product
        uses, but it computes them ignoring the values the visitor chose
        (`attribute_value_dict={}` when building `pavs_per_attribute`). Keeping
        the panel in sync with the chosen values is what this module adds, and
        the other tests no longer tell it apart from Odoo's own behaviour.

        Every display type this module overrides is checked: each one is
        rendered by a different template. `range`, new in 20.0, is left out:
        its slider is a continuous interval, so dropping the values in the
        middle would not narrow it down, it would break it.
        """
        slug = self.env["ir.http"]._slug
        # Only `product_template` is green, so `product_template_2` is left out
        url = (
            f"/shop?{slug(self.product_attribute)}"
            f"={slug(self.product_attribute_value_green)}"
        )
        attributes = (
            self.attribute_radio,
            self.attribute_radio_large,
            self.attribute_multi,
            self.attribute_multi_large,
            self.attribute_select,
            self.attribute_image,
            self.attribute_pills,
            self.attribute_color,
        )
        for attribute in attributes:
            with self.subTest(attribute=attribute.name):
                self.assertEqual(
                    self._rendered_values(attribute, url=url),
                    {attribute.value_ids[0].id},
                    "The value of the product filtered out should be gone",
                )

    def test_attribute_section_is_hidden_when_no_value_is_left(self):
        """An attribute left without any usable value is not rendered at all.

        Until 19.0 `attributes` was built from a domain that already had the
        chosen values applied, so such an attribute never reached the template.
        Since 20.0 it is built ignoring them, so without hiding the section the
        shop would show an attribute heading over an empty box.
        """
        # An attribute only the first product uses
        unused = self.env["product.attribute"].create(
            {
                "name": "Only On The First Product",
                "display_type": "radio",
                "create_variant": "no_variant",
                "value_ids": [(0, 0, {"name": "Only value"})],
            }
        )
        self.product_template.attribute_line_ids = [
            (0, 0, {"attribute_id": unused.id, "value_ids": [(4, unused.value_ids.id)]})
        ]
        slug = self.env["ir.http"]._slug
        # Only `product_template_2` is blue, so the first product is left out
        page = html.fromstring(
            self.url_open(
                f"/shop?{slug(self.product_attribute)}"
                f"={slug(self.product_attribute_value_blue)}"
            ).content
        )
        sections = page.xpath(
            """
            //form[contains(concat(" ", @class, " "), " js_attributes ")]
            //*[self::button or self::label or self::h2 or self::h6]
            """
        )
        self.assertNotIn(
            unused.name,
            " ".join(section.text_content() for section in sections),
            "The attribute has no value left to offer, its section should be gone",
        )

    def test_ui_website(self):
        # This test ensures that unused attributes are not visible in the filter panel.
        self.start_tour(
            "/shop",
            "website_sale_product_attribute_value_filter_existing",
            login="admin",
        )

    def test_ui_website_search_desk(self):
        # This test ensures that attributes not used in the products displayed after a
        # search are not visible in the filter panel.
        self.start_tour(
            "/shop?search=Alpha",
            "website_sale_product_attribute_value_filter_existing_search_desk",
            login="admin",
        )
