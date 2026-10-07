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
        cls.blocked_product = cls._create_product_with_blocking_informational_values()

    @classmethod
    def _create_product_with_blocking_informational_values(cls):
        """Return a product whose informational values exclude every variant.

        The product comes in Small and Large, and has two informational
        attributes with a single value each: Material "Cotton", excluded for
        Large, and Finish "Glossy", excluded for Small. As every combination
        needs both values, standard Odoo finds no possible combination at all.
        """
        finish_attribute = cls.env["product.attribute"].create(
            {
                "name": "Test Finish",
                "create_variant": "no_variant",
                "value_ids": [Command.create({"name": "Glossy"})],
            }
        )
        cotton = cls.informational_attribute.value_ids.filtered(
            lambda value: value.name == "Cotton"
        )
        product = cls.env["product.template"].create(
            {
                "name": "Test product with blocking informational values",
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
                            "value_ids": [Command.set(cotton.ids)],
                        }
                    ),
                    Command.create(
                        {
                            "attribute_id": finish_attribute.id,
                            "value_ids": [Command.set(finish_attribute.value_ids.ids)],
                        }
                    ),
                ],
            }
        )
        ptavs = product.attribute_line_ids.product_template_value_ids
        size_ptavs = ptavs.filtered(
            lambda ptav: ptav.attribute_id == cls.variant_attribute
        )
        for informational_name, size_name in (("Cotton", "Large"), ("Glossy", "Small")):
            ptavs.filtered(lambda ptav, n=informational_name: ptav.name == n).write(
                {
                    "exclude_for": [
                        Command.create(
                            {
                                "product_tmpl_id": product.id,
                                "value_ids": [
                                    Command.link(
                                        size_ptavs.filtered(
                                            lambda ptav, n=size_name: ptav.name == n
                                        ).id
                                    )
                                ],
                            }
                        )
                    ]
                }
            )
        return product

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

    def test_add_to_cart_possible_despite_informational_exclusions(self):
        """Hidden informational values do not make a product unsellable.

        Scenario:
            1. A product comes in Small and Large.
            2. Its informational values are each excluded for one of the
               sizes, so standard Odoo finds no possible combination.
        Expected:
            - The product can still be added to the cart.
        """
        product = self.blocked_product
        self.assertFalse(next(product._get_possible_combinations(), False))
        self.assertTrue(product._is_add_to_cart_possible())

    def test_add_to_cart_not_possible_without_any_possible_variant(self):
        """A product without any active variant still cannot be sold.

        Scenario:
            1. Take the product whose informational values exclude every
               variant.
            2. Archive all its variants, keeping the product itself active.
        Expected:
            - The product cannot be added to the cart.
        """
        product = self.blocked_product
        # A plain write, unlike `action_archive`, keeps the template active.
        product.product_variant_ids.write({"active": False})
        self.assertTrue(product.active)
        self.assertFalse(product._is_add_to_cart_possible())

    def test_combination_info_defaults_to_first_variant(self):
        """The product page opens on a sellable variant.

        Scenario:
            1. Open the page of the product whose informational values
               exclude every variant, without choosing any variant.
        Expected:
            - The page starts on one of the product's variants.
            - That variant can be added to the cart.
        """
        product = self.blocked_product
        with MockRequest(self.env, website=self.website):
            combination_info = product._get_combination_info()
        self.assertTrue(combination_info["is_combination_possible"])
        self.assertIn(combination_info["product_id"], product.product_variant_ids.ids)

    def test_first_possible_combination_falls_back_on_variant_values(self):
        """The first combination only picks the sizes when nothing else fits.

        Scenario:
            1. Ask for the first possible combination of the product whose
               informational values exclude every variant.
        Expected:
            - A combination is found.
            - It only holds a size, no informational value.
            - That size is possible when ignoring informational values.
        """
        product = self.blocked_product
        combination = product._get_first_possible_combination()
        self.assertTrue(combination)
        self.assertEqual(combination, combination._without_no_variant_attributes())
        self.assertTrue(
            product._is_combination_possible(combination, ignore_no_variant=True)
        )

    def test_first_possible_variant_falls_back_on_variant_values(self):
        """The shop grid, wishlist and comparison pages get a variant.

        Scenario:
            1. Ask for the first possible variant of the product whose
               informational values exclude every variant.
        Expected:
            - One of the product's variants is returned.
        """
        product = self.blocked_product
        self.assertIn(
            product._get_first_possible_variant_id(), product.product_variant_ids.ids
        )

    def test_first_possible_combination_keeps_necessary_values(self):
        """Required values are never dropped to find a combination.

        Scenario:
            1. Ask for the first possible combination of the product whose
               informational values exclude every variant, requiring the
               Finish "Glossy".
        Expected:
            - No combination is found, as standard Odoo would answer.
        """
        product = self.blocked_product
        glossy = product.attribute_line_ids.product_template_value_ids.filtered(
            lambda ptav: ptav.name == "Glossy"
        )
        self.assertFalse(
            product._get_first_possible_combination(necessary_values=glossy)
        )
