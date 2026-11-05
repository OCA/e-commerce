# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestUi(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Storable product",
                "type": "consu",
                "is_storable": True,
                "allow_out_of_stock_order": False,
                "is_published": True,
                "list_price": 10.0,
            }
        )
        stock_location = cls.env.ref("stock.stock_location_stock")
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, stock_location, 40.0
        )
        # 3 units reserved for a delivery
        picking_out = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 3.0,
                            "location_id": stock_location.id,
                            "location_dest_id": cls.env.ref(
                                "stock.stock_location_customers"
                            ).id,
                        },
                    )
                ],
            }
        )
        picking_out.action_assign()
        # 5 units ready to be received
        picking_in = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 5.0,
                            "location_id": cls.env.ref(
                                "stock.stock_location_suppliers"
                            ).id,
                            "location_dest_id": stock_location.id,
                        },
                    )
                ],
            }
        )
        picking_in.action_assign()

    def test_add_to_cart_available_quantity(self):
        """The shop accepts in the cart the quantity it shows as available"""
        self.assertEqual(self.product.free_qty, 37)
        self.assertEqual(self.product.immediately_usable_qty, 42)
        self.start_tour("/shop?search=Storable product", "website_sale_stock_available")
