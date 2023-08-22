# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.exceptions import UserError
from odoo.tests import SavepointCase


class TestProduct(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tmpl = cls.env.ref("product.product_product_4_product_template")
        cls.product_sw = cls.env.ref("product.product_product_4")  # steel, white
        cls.product_sb = cls.env.ref("product.product_product_4b")  # steel, black
        cls.product_aw = cls.env.ref("product.product_product_4c")  # aluminium, white
        cls.attr_a = cls.env.ref("product.product_attribute_value_2")  # aluminium
        cls.attr_s = cls.env.ref("product.product_attribute_value_1")  # steel
        cls.attr_w = cls.env.ref("product.product_attribute_value_3")  # white

    def test_product_alias(self):
        alias_a = self.env["product.alias"].create(
            {
                "name": "Aluminium Chair",
                "product_tmpl_id": self.tmpl.id,
                "attribute_value_ids": [(6, 0, [self.attr_a.id])],
            }
        )
        self.assertEqual(alias_a, self.product_aw.alias_id)
        self.assertFalse(self.product_sw.alias_id)
        self.assertFalse(self.product_sb.alias_id)

        alias_s = self.env["product.alias"].create(
            {
                "name": "Steel Chair",
                "product_tmpl_id": self.tmpl.id,
                "attribute_value_ids": [(6, 0, [self.attr_s.id])],
            }
        )
        self.assertEqual(alias_a, self.product_aw.alias_id)
        self.assertEqual(alias_s, self.product_sw.alias_id)
        self.assertEqual(alias_s, self.product_sb.alias_id)

    def test_product_alias_two_value(self):
        alias_sw = self.env["product.alias"].create(
            {
                "name": "Steel Chair White",
                "product_tmpl_id": self.tmpl.id,
                "attribute_value_ids": [(6, 0, [self.attr_s.id, self.attr_w.id])],
            }
        )
        self.assertEqual(alias_sw, self.product_sw.alias_id)
        self.assertFalse(self.product_aw.alias_id)
        self.assertFalse(self.product_sb.alias_id)

    def test_product_alias_raise(self):
        self.env["product.alias"].create(
            {
                "name": "Aluminium Chair",
                "product_tmpl_id": self.tmpl.id,
                "attribute_value_ids": [(6, 0, [self.attr_a.id])],
            }
        )
        with self.assertRaises(UserError):
            self.env["product.alias"].create(
                {
                    "name": "Aluminium Chair 2",
                    "product_tmpl_id": self.tmpl.id,
                    "attribute_value_ids": [(6, 0, [self.attr_a.id])],
                }
            )
            self.env["product.alias"].flush()
