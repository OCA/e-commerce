from odoo.tests import TransactionCase


class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_id = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "website_sale_min_qty": 2.0,
                "website_sale_max_qty": 5.0,
                "sale_ok": True,
                "website_published": True,
            }
        )
        cls.partner_id = cls.env["res.partner"].create(
            {"name": "Test Partner", "email": "test"}
        )
        cls.order_id = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_id.id,
                "order_line": [
                    (0, 0, {"product_id": cls.product_id.id, "product_uom_qty": 2})
                ],
            }
        )

    def test_verify_update_quantity(self):

        line = self.order_id.order_line[0]
        self.assertEqual(line.product_uom_qty, 2)
        res = self.order_id._verify_updated_quantity(line, self.product_id, 7)
        self.assertEqual(res[0], 5)
        self.assertEqual(res[1], "maxquantity")
