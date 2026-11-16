# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestStockAvailability(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "is_storable": True,
            }
        )

        cls.supplier = cls.env["res.partner"].create(
            {
                "name": "Supplier",
            }
        )

        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "inventory_quantity": 10.0,
                "location_id": cls.env.ref("stock.warehouse0").lot_stock_id.id,
                "product_id": cls.product.id,
            }
        )._apply_inventory()

    def test_sold_out(self):
        self.assertFalse(self.product._is_sold_out())

        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "inventory_quantity": 0.0,
                "location_id": self.env.ref("stock.warehouse0").lot_stock_id.id,
                "product_id": self.product.id,
            }
        )._apply_inventory()

        self.assertTrue(self.product._is_sold_out())

        seller = self.env["product.supplierinfo"].create(
            {
                "product_id": self.product.id,
                "partner_id": self.supplier.id,
                "stock_availability": "available",
            }
        )
        self.assertFalse(self.product._is_sold_out())

        seller.stock_availability = "unavailable"

        self.assertTrue(self.product._is_sold_out())
