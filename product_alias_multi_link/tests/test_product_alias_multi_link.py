# Copyright 2025 Akretion (http://www.akretion.com).
# @author Sébastien Alix <sebastien.alix@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestProductAliasMultiLink(BaseCommon):
    """Test product template links with alias support"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductTemplateLink = cls.env["product.template.link"]
        cls.ProductAlias = cls.env["product.alias"]
        cls.ProductTemplate = cls.env["product.template"]
        # Get test products
        cls.product_product_1 = cls.env.ref("product.product_product_1")
        cls.product_product_2 = cls.env.ref("product.product_product_2")
        cls.product_tmpl_1 = cls.product_product_1.product_tmpl_id
        cls.product_tmpl_2 = cls.product_product_2.product_tmpl_id
        # Get test link type
        cls.link_type = cls.env.ref(
            "product_template_multi_link.product_template_link_type_cross_selling"
        )
        # Get attributes for product_product_4
        cls.tmpl_with_attrs = cls.env.ref("product.product_product_4_product_template")
        cls.product_sw = cls.env.ref("product.product_product_4")  # steel, white
        cls.product_sb = cls.env.ref("product.product_product_4b")  # steel, black
        cls.product_aw = cls.env.ref("product.product_product_4c")  # aluminium, white
        cls.attr_a = cls.env.ref("product.product_attribute_value_2")  # aluminium
        cls.attr_s = cls.env.ref("product.product_attribute_value_1")  # steel
        cls.attr_w = cls.env.ref("product.product_attribute_value_3")  # white

    def _create_link_with_aliases(
        self,
        left_tmpl,
        left_alias,
        right_tmpl,
        right_alias,
        left_prod=None,
        right_prod=None,
    ):
        """Helper to create a link with aliases"""
        values = {
            "left_product_tmpl_id": left_tmpl.id,
            "left_product_alias_id": left_alias.id,
            "right_product_tmpl_id": right_tmpl.id,
            "right_product_alias_id": right_alias.id,
            "type_id": self.link_type.id,
        }
        if left_prod:
            values["left_product_id"] = left_prod.id
        if right_prod:
            values["right_product_id"] = right_prod.id
        link = self.ProductTemplateLink.create(values)
        link.flush_recordset()
        return link

    def test_create_link_with_aliases_only(self):
        """
        Data:
            - 2 product templates with aliases
        Test Case:
            - Create a link between two aliases
        Expected result:
            - Link is created successfully
        """
        # Create aliases
        alias_a = self.ProductAlias.create(
            {
                "name": "Aluminium Variant",
                "product_tmpl_id": self.tmpl_with_attrs.id,
                "attribute_value_ids": [(6, 0, [self.attr_a.id])],
            }
        )
        alias_s = self.ProductAlias.create(
            {
                "name": "Steel Variant",
                "product_tmpl_id": self.tmpl_with_attrs.id,
                "attribute_value_ids": [(6, 0, [self.attr_s.id])],
            }
        )
        # Create a link with aliases only (no error)
        self._create_link_with_aliases(
            self.tmpl_with_attrs,
            alias_a,
            self.tmpl_with_attrs,
            alias_s,
        )

    def test_create_link_with_products_and_aliases(self):
        """
        Data:
            - 2 product templates
            - Products with associated aliases
        Test Case:
            - Create a link with both products and aliases
        Expected result:
            - Link is created with all fields populated
        """
        # Create aliases
        alias_a = self.ProductAlias.create(
            {
                "name": "Aluminium Variant",
                "product_tmpl_id": self.tmpl_with_attrs.id,
                "attribute_value_ids": [(6, 0, [self.attr_a.id])],
            }
        )
        alias_s = self.ProductAlias.create(
            {
                "name": "Steel Variant",
                "product_tmpl_id": self.tmpl_with_attrs.id,
                "attribute_value_ids": [(6, 0, [self.attr_s.id])],
            }
        )
        # Create a link with products and aliases (no error)
        self._create_link_with_aliases(
            self.tmpl_with_attrs,
            alias_a,
            self.tmpl_with_attrs,
            alias_s,
            left_prod=self.product_aw,
            right_prod=self.product_sw,
        )

    def test_identical_link_with_aliases_rejected(self):
        """
        Data:
            - 2 product templates with aliases
        Test Case:
            - Create a link between two aliases
            - Try to create the same link with aliases
        Expected result:
            - ValidationError is raised for identical link
        """
        # Create aliases
        alias_a = self.ProductAlias.create(
            {
                "name": "Aluminium Variant",
                "product_tmpl_id": self.tmpl_with_attrs.id,
                "attribute_value_ids": [(6, 0, [self.attr_a.id])],
            }
        )
        alias_s = self.ProductAlias.create(
            {
                "name": "Steel Variant",
                "product_tmpl_id": self.tmpl_with_attrs.id,
                "attribute_value_ids": [(6, 0, [self.attr_s.id])],
            }
        )
        # Create first link
        link = self._create_link_with_aliases(
            self.tmpl_with_attrs,
            alias_a,
            self.tmpl_with_attrs,
            alias_s,
        )
        # Try to copy link (should fail as it creates a duplicate)
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            link.copy()

    def test_inverse_link_with_aliases_rejected(self):
        """
        Data:
            - 2 product templates with aliases
        Test Case:
            - Create a link between alias_a -> alias_s
            - Try to create inverse link alias_s -> alias_a
        Expected result:
            - ValidationError is raised for inverse link
        """
        # Create aliases
        alias_a = self.ProductAlias.create(
            {
                "name": "Aluminium Variant",
                "product_tmpl_id": self.tmpl_with_attrs.id,
                "attribute_value_ids": [(6, 0, [self.attr_a.id])],
            }
        )
        alias_s = self.ProductAlias.create(
            {
                "name": "Steel Variant",
                "product_tmpl_id": self.tmpl_with_attrs.id,
                "attribute_value_ids": [(6, 0, [self.attr_s.id])],
            }
        )
        # Create first link
        self._create_link_with_aliases(
            self.tmpl_with_attrs,
            alias_a,
            self.tmpl_with_attrs,
            alias_s,
        )
        # Try to create inverse link
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self._create_link_with_aliases(
                self.tmpl_with_attrs,
                alias_s,
                self.tmpl_with_attrs,
                alias_a,
            )

    def test_alias_link_ids_both_sides(self):
        """
        Data:
            - Two aliases (A, B)
        Test Case:
            - Create link A->B
            - Get product_alias_link_ids from both aliases
        Expected result:
            - Both aliases see the same link in their computed field
        """
        alias_a = self.ProductAlias.create(
            {
                "name": "Aluminium",
                "product_tmpl_id": self.tmpl_with_attrs.id,
                "attribute_value_ids": [(6, 0, [self.attr_a.id])],
            }
        )
        alias_s = self.ProductAlias.create(
            {
                "name": "Steel",
                "product_tmpl_id": self.tmpl_with_attrs.id,
                "attribute_value_ids": [(6, 0, [self.attr_s.id])],
            }
        )
        link = self._create_link_with_aliases(
            self.tmpl_with_attrs,
            alias_a,
            self.tmpl_with_attrs,
            alias_s,
        )
        # Both aliases should see the link
        self.assertIn(link, alias_a.product_alias_link_ids)
        self.assertIn(link, alias_s.product_alias_link_ids)

    def test_link_cache_invalidation_on_unlink(self):
        """
        Data:
            - 2 product templates with aliases
        Test Case:
            - Create a link between two aliases
            - Verify aliases have the link in their computed field
            - Unlink the link
        Expected result:
            - Aliases' product_alias_link_ids cache is invalidated
        """
        # Create aliases
        alias_a = self.ProductAlias.create(
            {
                "name": "Aluminium Variant",
                "product_tmpl_id": self.tmpl_with_attrs.id,
                "attribute_value_ids": [(6, 0, [self.attr_a.id])],
            }
        )
        alias_s = self.ProductAlias.create(
            {
                "name": "Steel Variant",
                "product_tmpl_id": self.tmpl_with_attrs.id,
                "attribute_value_ids": [(6, 0, [self.attr_s.id])],
            }
        )
        # Create link
        link = self._create_link_with_aliases(
            self.tmpl_with_attrs,
            alias_a,
            self.tmpl_with_attrs,
            alias_s,
        )
        # Verify link is in aliases' computed field
        self.assertIn(link, alias_a.product_alias_link_ids)
        self.assertIn(link, alias_s.product_alias_link_ids)
        # Unlink the link (cache should be invalidated)
        link.unlink()
        # Verify link is removed from aliases' computed field
        self.assertNotIn(link, alias_a.product_alias_link_ids)
        self.assertNotIn(link, alias_s.product_alias_link_ids)
