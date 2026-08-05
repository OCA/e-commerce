# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.fields import Command
from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestWebsiteSaleComparisonSpecificationExclusion(TransactionCase):
    def test_display_value_ids_ignores_variant_defining_lines(self):
        """A variant-defining attribute must keep listing all of its
        values in the specs table, even if some values are excluded for
        other values of the current combination (e.g. Legs: Aluminium
        excludes Color: Black) -- that exclusion only restricts which
        variants exist, it must not hide "Black" from the specs overview,
        since the product is still offered in that color."""
        legs_attribute = self.env["product.attribute"].create(
            {
                "name": "Legs",
                "value_ids": [
                    Command.create({"name": "Steel"}),
                    Command.create({"name": "Aluminium"}),
                ],
            }
        )
        color_attribute = self.env["product.attribute"].create(
            {
                "name": "Color",
                "value_ids": [
                    Command.create({"name": "White"}),
                    Command.create({"name": "Black"}),
                ],
            }
        )
        product = self.env["product.template"].create(
            {
                "name": "Desk",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": legs_attribute.id,
                            "value_ids": [Command.set(legs_attribute.value_ids.ids)],
                        }
                    ),
                    Command.create(
                        {
                            "attribute_id": color_attribute.id,
                            "value_ids": [Command.set(color_attribute.value_ids.ids)],
                        }
                    ),
                ],
            }
        )
        legs_line, color_line = product.attribute_line_ids
        steel, aluminium = legs_line.product_template_value_ids
        white, black = color_line.product_template_value_ids
        aluminium.exclude_for = [
            Command.create(
                {
                    "product_tmpl_id": product.id,
                    "value_ids": [Command.link(black.id)],
                }
            )
        ]

        displayed = color_line._get_display_value_ids(aluminium)

        self.assertEqual(
            displayed,
            white.product_attribute_value_id | black.product_attribute_value_id,
        )

    def test_display_value_ids_ignores_unrelated_conflicts_in_combination(self):
        """A non-variant-defining line with no `exclude_for` of its own must
        keep showing all of its values, even when the rest of the given
        combination is itself internally conflicting (e.g. two mutually
        exclusive variant-defining values were both selected). The
        unrelated conflict must not be mistaken for a conflict involving
        this line's own candidates."""
        color_attribute = self.env["product.attribute"].create(
            {
                "name": "Color",
                "value_ids": [
                    Command.create({"name": "Red"}),
                ],
            }
        )
        size_attribute = self.env["product.attribute"].create(
            {
                "name": "Size",
                "value_ids": [
                    Command.create({"name": "1"}),
                    Command.create({"name": "2"}),
                ],
            }
        )
        note_attribute = self.env["product.attribute"].create(
            {
                "name": "Note",
                "create_variant": "no_variant",
                "value_ids": [
                    Command.create({"name": "Hello"}),
                    Command.create({"name": "World"}),
                ],
            }
        )
        product = self.env["product.template"].create(
            {
                "name": "Sample",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": color_attribute.id,
                            "value_ids": [Command.set(color_attribute.value_ids.ids)],
                        }
                    ),
                    Command.create(
                        {
                            "attribute_id": size_attribute.id,
                            "value_ids": [Command.set(size_attribute.value_ids.ids)],
                        }
                    ),
                    Command.create(
                        {
                            "attribute_id": note_attribute.id,
                            "value_ids": [Command.set(note_attribute.value_ids.ids)],
                        }
                    ),
                ],
            }
        )
        color_line, size_line, note_line = product.attribute_line_ids
        red = color_line.product_template_value_ids
        size_1, size_2 = size_line.product_template_value_ids
        hello, world = note_line.product_template_value_ids
        # Red and Size 1 mutually exclude each other; Note has no
        # exclude_for of its own at all.
        red.exclude_for = [
            Command.create(
                {
                    "product_tmpl_id": product.id,
                    "value_ids": [Command.link(size_1.id)],
                }
            )
        ]
        size_1.exclude_for = [
            Command.create(
                {
                    "product_tmpl_id": product.id,
                    "value_ids": [Command.link(red.id)],
                }
            )
        ]

        displayed = note_line._get_display_value_ids(red + size_1 + hello)

        self.assertEqual(
            displayed,
            hello.product_attribute_value_id | world.product_attribute_value_id,
        )

    @classmethod
    def _create_sized_product_with_weight_exclusions(cls):
        """A product with a Size (variant-defining) line and a Weight
        (non-variant-defining) line whose two values each exclude the
        opposite Size value -- the fixture shared by the tests below."""
        size_attribute = cls.env["product.attribute"].create(
            {
                "name": "Size",
                "value_ids": [
                    Command.create({"name": "Size 1"}),
                    Command.create({"name": "Size 2"}),
                ],
            }
        )
        weight_attribute = cls.env["product.attribute"].create(
            {
                "name": "Weight",
                "create_variant": "no_variant",
                "value_ids": [
                    Command.create({"name": "Weight for Size 1"}),
                    Command.create({"name": "Weight for Size 2"}),
                ],
            }
        )
        product = cls.env["product.template"].create(
            {
                "name": "Sized product",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": size_attribute.id,
                            "value_ids": [Command.set(size_attribute.value_ids.ids)],
                        }
                    ),
                    Command.create(
                        {
                            "attribute_id": weight_attribute.id,
                            "value_ids": [Command.set(weight_attribute.value_ids.ids)],
                        }
                    ),
                ],
            }
        )
        size_line, weight_line = product.attribute_line_ids
        size_1, size_2 = size_line.product_template_value_ids
        weight_1, weight_2 = weight_line.product_template_value_ids
        weight_1.exclude_for = [
            Command.create(
                {
                    "product_tmpl_id": product.id,
                    "value_ids": [Command.link(size_2.id)],
                }
            )
        ]
        weight_2.exclude_for = [
            Command.create(
                {
                    "product_tmpl_id": product.id,
                    "value_ids": [Command.link(size_1.id)],
                }
            )
        ]
        return product, size_1, size_2, weight_line, weight_1, weight_2

    def test_display_value_ids_excludes_incompatible_values(self):
        """A non-variant-defining attribute value excluded for a given
        variant-defining combination must not be returned for display."""
        _product, size_1, size_2, weight_line, weight_1, weight_2 = (
            self._create_sized_product_with_weight_exclusions()
        )

        displayed_for_size_1 = weight_line._get_display_value_ids(size_1)
        displayed_for_size_2 = weight_line._get_display_value_ids(size_2)

        self.assertEqual(displayed_for_size_1, weight_1.product_attribute_value_id)
        self.assertEqual(displayed_for_size_2, weight_2.product_attribute_value_id)

    def test_get_specs_table_html_recomputes_by_combination(self):
        """`_get_specs_table_html` must return content matching the given
        combination, so the front-end can refresh the specs table when the
        customer changes variant."""
        product, size_1, size_2, _weight_line, weight_1, weight_2 = (
            self._create_sized_product_with_weight_exclusions()
        )

        specs_size_1 = product._get_specs_table_html(size_1 + weight_1)
        specs_size_2 = product._get_specs_table_html(size_2 + weight_2)

        self.assertIn("Weight for Size 1", specs_size_1)
        self.assertNotIn("Weight for Size 2", specs_size_1)
        self.assertIn("Weight for Size 2", specs_size_2)
        self.assertNotIn("Weight for Size 1", specs_size_2)
