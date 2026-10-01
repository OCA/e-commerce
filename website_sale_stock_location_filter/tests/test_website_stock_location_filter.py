# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestWebsiteStockLocationFilter(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.stock_location = cls.warehouse.lot_stock_id
        # Technician location is a *child* of the warehouse stock location, so
        # excluding it also exercises the `strict` no-child-re-expansion path.
        cls.technician_location = cls.env["stock.location"].create(
            {
                "name": "Technician",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Storable Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.website = cls.env["website"].search([], limit=1)
        cls.website.warehouse_id = cls.warehouse
        Quant = cls.env["stock.quant"]
        Quant._update_available_quantity(cls.product, cls.stock_location, 10.0)
        Quant._update_available_quantity(cls.product, cls.technician_location, 5.0)

    def test_all_locations_included_by_default(self):
        qty = self.website._get_product_available_qty(self.product)
        self.assertEqual(qty, 15.0, "Both internal locations should be counted")

    def test_excluded_child_location_not_counted(self):
        self.technician_location.exclude_from_website_stock = True
        qty = self.website._get_product_available_qty(self.product)
        self.assertEqual(
            qty,
            10.0,
            "Excluded child location must not be re-included via its parent",
        )

    def test_reserved_quantity_is_subtracted(self):
        # free_qty must remain the basis: reserve 3 from the visible stock.
        self.env["stock.quant"]._update_reserved_quantity(
            self.product, self.stock_location, 3.0
        )
        self.technician_location.exclude_from_website_stock = True
        qty = self.website._get_product_available_qty(self.product)
        self.assertEqual(qty, 7.0, "Reserved quantity must be subtracted (free_qty)")
