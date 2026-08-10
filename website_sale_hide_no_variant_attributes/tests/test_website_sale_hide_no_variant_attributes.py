# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import Command
from odoo.tests import TransactionCase

from odoo.addons.website_sale.tests.common import MockRequest


class TestWebsiteSaleHideNoVariantAttributes(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.variant_attribute = cls.env["product.attribute"].create(
            {
                "name": "Test Size",
                "create_variant": "always",
                "value_ids": [
                    Command.create({"name": "Small"}),
                    Command.create({"name": "Large"}),
                ],
            }
        )
        cls.informational_attribute = cls.env["product.attribute"].create(
            {
                "name": "Test Material",
                "create_variant": "no_variant",
                "value_ids": [
                    Command.create({"name": "Cotton"}),
                    Command.create({"name": "Wool"}),
                ],
            }
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "Test product with mixed attributes",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.variant_attribute.id,
                            "value_ids": [
                                Command.set(cls.variant_attribute.value_ids.ids)
                            ],
                        }
                    ),
                    Command.create(
                        {
                            "attribute_id": cls.informational_attribute.id,
                            "value_ids": [
                                Command.set(cls.informational_attribute.value_ids.ids)
                            ],
                        }
                    ),
                ],
            }
        )
        cls.variant_ptav_large = cls.product.attribute_line_ids.filtered(
            lambda line: line.attribute_id == cls.variant_attribute
        ).product_template_value_ids.filtered(lambda ptav: ptav.name == "Large")
        cls.informational_ptav_wool = cls.product.attribute_line_ids.filtered(
            lambda line: line.attribute_id == cls.informational_attribute
        ).product_template_value_ids.filtered(lambda ptav: ptav.name == "Wool")
        cls.informational_ptav_wool.exclude_for = [
            Command.create(
                {
                    "product_tmpl_id": cls.product.id,
                    "value_ids": [Command.link(cls.variant_ptav_large.id)],
                }
            )
        ]
        cls.website = cls.env["website"].get_current_website()

    def test_exclusions_ignore_informational_attribute(self):
        exclusions = self.product._get_attribute_exclusions()["exclusions"]
        self.assertIn(self.informational_ptav_wool.id, exclusions)
        self.assertEqual(exclusions[self.informational_ptav_wool.id], [])
        for excluded_ids in exclusions.values():
            self.assertNotIn(self.variant_ptav_large.id, excluded_ids)

    def test_mapped_attribute_names_ignore_informational_attribute(self):
        mapped_names = self.product._get_attribute_exclusions()[
            "mapped_attribute_names"
        ]
        self.assertNotIn(self.informational_ptav_wool.id, mapped_names)
        self.assertIn(self.variant_ptav_large.id, mapped_names)

    def test_combination_info_ignores_missing_informational_attribute(self):
        # Mimics a combination check triggered after page load: since the
        # informational attribute's input is never rendered, the browser can
        # never submit a value for it again, so the combination only carries
        # the variant-defining value.
        with MockRequest(self.env, website=self.website):
            combination_info = self.product._get_combination_info(
                combination=self.variant_ptav_large
            )
        self.assertTrue(combination_info["is_combination_possible"])

    def test_combination_info_ignores_conflicting_informational_default(self):
        # Mimics the very first page render, where the server still picks a
        # default value for the hidden informational attribute; here that
        # default happens to be the "Wool" value excluded by the rule above.
        combination = self.variant_ptav_large | self.informational_ptav_wool
        with MockRequest(self.env, website=self.website):
            combination_info = self.product._get_combination_info(
                combination=combination
            )
        self.assertTrue(combination_info["is_combination_possible"])
