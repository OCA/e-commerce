# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestProductTemplateLink(SavepointCase):
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

    def test_01(self):
        """
        Data:
            - 2 publication templates
        Test Case:
            - Try to create 2 links of same type
        Expected result:
            - ValidationError is raised
        """
        link1 = self.ProductTemplateLink.create(
            {
                "left_product_tmpl_id": self.product_product_1.id,
                "right_product_tmpl_id": self.product_product_2.id,
                "type_id": self.link_type.id,
            }
        )
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            link1.copy()

        # create the same link but inverse ids
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.ProductTemplateLink.create(
                {
                    "left_product_tmpl_id": self.product_product_2.id,
                    "right_product_tmpl_id": self.product_product_1.id,
                    "type_id": self.link_type.id,
                }
            )

    def test_02(self):
        """
        Data:
            - 1 publication templates
        Test Case:
            - Try to create 1 link between the same product
        Expected result:
            - ValidationError is raised
        """
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.ProductTemplateLink.create(
                {
                    "left_product_tmpl_id": self.product_product_1.id,
                    "right_product_tmpl_id": self.product_product_1.id,
                    "type_id": self.link_type.id,
                }
            )

    def test_03(self):
        """
        Data:
            - 2 publication templates
        Test Case:
            - Create 1 link between the 2 products
        Expected result:
            - The link is visible from the 2 products
        """
        link1 = self.ProductTemplateLink.create(
            {
                "left_product_tmpl_id": self.product_product_1.id,
                "right_product_tmpl_id": self.product_product_2.id,
                "type_id": self.link_type.id,
            }
        )
        self.assertEqual(link1, self.product_product_1.product_template_link_ids)

        self.assertEqual(link1, self.product_product_2.product_template_link_ids)

    def test_04(self):
        """
        Data:
            - 2 publication templates
        Test Case:
            1 Create 1 link between the 2 products
            2 Unlik the link
        Expected result:
            1 The link is visible from the 2 products
            2 No link remains between the 2 products
        This test check the cache invalidation of the computed fields on the
        product.template
        """
        link1 = self.ProductTemplateLink.create(
            {
                "left_product_tmpl_id": self.product_product_1.id,
                "right_product_tmpl_id": self.product_product_2.id,
                "type_id": self.link_type.id,
            }
        )
        self.assertEqual(link1, self.product_product_1.product_template_link_ids)

        self.assertEqual(link1, self.product_product_2.product_template_link_ids)

        self.assertEqual(1, self.product_product_1.product_template_link_count)
        self.assertEqual(1, self.product_product_2.product_template_link_count)

        link1.unlink()
        self.assertFalse(self.product_product_1.product_template_link_ids)
        self.assertFalse(self.product_product_2.product_template_link_ids)
        self.assertEqual(0, self.product_product_1.product_template_link_count)
        self.assertEqual(0, self.product_product_2.product_template_link_count)
