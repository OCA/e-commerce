# Copyright 2025 Simone Rubino - PyTech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import tests


@tests.tagged("post_install", "-at_install")
class TestReferenceDisplayed(tests.HttpSavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        attribute_form = tests.Form(cls.env["product.attribute"])
        attribute_form.name = "Test dynamic variant attribute"
        attribute_form.create_variant = "always"
        with attribute_form.value_ids.new() as value:
            value.name = "Test dynamic variant value 1"
        with attribute_form.value_ids.new() as value:
            value.name = "Test dynamic variant value 2"
        cls.attribute = attribute_form.save()
        cls.attribute_value_1, cls.attribute_value_2 = cls.attribute.value_ids

        product_template_form = tests.Form(cls.env["product.template"])
        product_template_form.name = "Test dynamic variant product template"
        product_template_form.list_price = 100
        product_template_form.is_published = True
        with product_template_form.attribute_line_ids.new() as length_attribute_line:
            length_attribute_line.attribute_id = cls.attribute
            for value in cls.attribute.value_ids:
                length_attribute_line.value_ids.add(value)
        cls.product_template = product_template_form.save()

        cls.product_variant_1 = cls.product_template.product_variant_ids.filtered(
            lambda variant, attribute_value=cls.attribute_value_1: attribute_value
            == variant.product_template_attribute_value_ids.product_attribute_value_id
        )
        cls.product_variant_1.default_code = "TESTREF1"
        cls.product_variant_2 = cls.product_template.product_variant_ids.filtered(
            lambda variant, attribute_value=cls.attribute_value_2: attribute_value
            == variant.product_template_attribute_value_ids.product_attribute_value_id
        )
        cls.product_variant_2.default_code = "TESTREF2"

    def test_dynamic_variant_reference(self):
        """When the selected variant changes, the Internal Reference is updated."""
        self.start_tour(
            "/",
            "tour_dynamic_variant_reference",
        )
