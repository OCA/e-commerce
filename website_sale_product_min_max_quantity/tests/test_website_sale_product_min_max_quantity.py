# Copyright 2023 Binhex - Nicolás Ramos <n.ramos@binhex.cloud>
# Copyright 2024 Binhex - Adasat Torres de León <a.torres@binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import HttpCase, TransactionCase


class TestWebsiteSaleProductMinMaxQuantity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "Product Test",
                "website_sale_min_qty": 2.0,
                "website_sale_max_qty": 5.0,
                "sale_ok": True,
                "website_published": True,
            }
        )

    def test_browse_product(self):
        product_id = self.product_template.id
        self.assertTrue(self.env["product.template"].browse(product_id))

    def test_add_quantity(self):
        min_qty = self.product_template.website_sale_min_qty
        max_qty = self.product_template.website_sale_max_qty
        add_qty = 1
        self.assertNotEqual(add_qty, min_qty)
        self.assertNotEqual(add_qty, max_qty)
        add_qty = min_qty
        self.assertEqual(add_qty, min_qty)
        add_qty = max_qty
        self.assertEqual(add_qty, max_qty)

    def test_min_max_quantity(self):
        min_qty = self.product_template.website_sale_min_qty
        max_qty = self.product_template.website_sale_max_qty
        self.assertEqual(min_qty, self.product_template.website_sale_min_qty)
        self.assertEqual(max_qty, self.product_template.website_sale_max_qty)
        self.product_template.website_sale_min_qty = 6.0
        self.product_template.website_sale_max_qty = 19.0
        self.assertEqual(self.product_template.website_sale_min_qty, 6.0)
        self.assertEqual(self.product_template.website_sale_max_qty, 19.0)


class TestWebsiteSale(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "Product Test",
                "website_sale_min_qty": 2.0,
                "website_sale_max_qty": 5.0,
                "sale_ok": True,
                "website_published": True,
            }
        )
