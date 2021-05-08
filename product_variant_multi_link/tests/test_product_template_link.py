# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestProductVariantLink(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.ProductTemplateLink = cls.env["product.template.link"]
        cls.product_product_1 = cls.env.ref("product.product_product_1")
        cls.product_product_2 = cls.env.ref("product.product_product_2")
        cls.link_type = cls.env.ref(
            "product_template_multi_link.product_template_link_type_cross_selling"
        )

    def _create_link_default(self):
        return self.ProductTemplateLink.create(
            {
                "left_product_tmpl_id": self.product_product_1.product_tmpl_id.id,
                "left_product_id": self.product_product_1.id,
                "right_product_tmpl_id": self.product_product_2.product_tmpl_id.id,
                "right_product_id": self.product_product_2.id,
                "type_id": self.link_type.id,
            }
        )

    def test_variants_required(self):
        with self.assertRaises(ValidationError) as err:
            self.ProductTemplateLink.create(
                {
                    "left_product_tmpl_id": self.product_product_1.product_tmpl_id.id,
                    "right_product_tmpl_id": self.product_product_2.product_tmpl_id.id,
                    "type_id": self.link_type.id,
                }
            )
        self.assertEqual(err.exception.name, "Source and target variants are required!")

    def test_duplicated_link_different_product(self):
        link1 = self._create_link_default()
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            link1.copy()

        # create the same link but inverse
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.ProductTemplateLink.create(
                {
                    "left_product_tmpl_id": self.product_product_2.product_tmpl_id.id,
                    "left_product_id": self.product_product_2.id,
                    "right_product_tmpl_id": self.product_product_1.product_tmpl_id.id,
                    "right_product_id": self.product_product_1.id,
                    "type_id": self.link_type.id,
                }
            )

    def test_duplicated_link_same_product(self):
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.ProductTemplateLink.create(
                {
                    "left_product_tmpl_id": self.product_product_1.product_tmpl_id.id,
                    "left_product_id": self.product_product_1.id,
                    "right_product_tmpl_id": self.product_product_1.product_tmpl_id.id,
                    "right_product_id": self.product_product_1.id,
                    "type_id": self.link_type.id,
                }
            )

    def test_product_variant_link_ids(self):
        link1 = self._create_link_default()
        self.assertIn(link1, self.product_product_1.product_template_link_ids)
        self.assertIn(link1, self.product_product_2.product_template_link_ids)
        self.assertIn(link1, self.product_product_1.product_variant_link_ids)
        self.assertIn(link1, self.product_product_2.product_variant_link_ids)

    def test_cache_invalidation(self):
        link1 = self._create_link_default()
        self.assertIn(link1, self.product_product_1.product_variant_link_ids)
        self.assertIn(link1, self.product_product_2.product_variant_link_ids)

        link1.unlink()
        self.assertNotIn(link1, self.product_product_1.product_variant_link_ids)
        self.assertNotIn(link1, self.product_product_2.product_variant_link_ids)

    def test_product_variant_links(self):
        link1 = self._create_link_default()
        self.assertIn(link1, self.product_product_1.product_variant_link_ids)
        self.assertIn(link1, self.product_product_2.product_variant_link_ids)
        self.assertEqual(self.product_product_1.product_product_link_count, 1)
        self.assertEqual(self.product_product_2.product_product_link_count, 1)

        link1.unlink()
        self.assertNotIn(link1, self.product_product_1.product_variant_link_ids)
        self.assertNotIn(link1, self.product_product_2.product_variant_link_ids)
        self.assertEqual(self.product_product_1.product_product_link_count, 0)
        self.assertEqual(self.product_product_1.product_product_link_count, 0)
