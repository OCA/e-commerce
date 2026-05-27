# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

from odoo.tests.common import TransactionCase


class SaleStockAvailableInfoPopup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(SaleStockAvailableInfoPopup, cls).setUpClass()
        user_group_stock_user = cls.env.ref("stock.group_stock_user")
        cls.user_stock_user = cls.env["res.users"].create(
            {
                "name": "Pauline Poivraisselle",
                "login": "pauline",
                "email": "p.p@example.com",
                "notification_type": "inbox",
                "groups_id": [(6, 0, [user_group_stock_user.id])],
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Storable product",
                "type": "product",
            }
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customers_location = cls.env.ref("stock.stock_location_customers")
        cls.suppliers_location = cls.env.ref("stock.stock_location_suppliers")
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.stock_location.id,
                "quantity": 40.0,
            }
        )
        cls.picking_out = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customers_location.id,
            }
        )
        cls.env["stock.move"].create(
            {
                "name": "a move",
                "product_id": cls.product.id,
                "product_uom_qty": 3.0,
                "product_uom": cls.product.uom_id.id,
                "picking_id": cls.picking_out.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customers_location.id,
            }
        )
        cls.picking_in = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.suppliers_location.id,
                "location_dest_id": cls.stock_location.id,
            }
        )
        cls.env["stock.move"].create(
            {
                "restrict_partner_id": cls.user_stock_user.partner_id.id,
                "name": "another move",
                "product_id": cls.product.id,
                "product_uom_qty": 5.0,
                "product_uom": cls.product.uom_id.id,
                "picking_id": cls.picking_in.id,
                "location_id": cls.suppliers_location.id,
                "location_dest_id": cls.stock_location.id,
            }
        )

    def test_get_combination_info(self):
        product_tmpl = self.product.product_tmpl_id
        combination_info = product_tmpl.with_context(
            website_sale_stock_get_quantity=True,
        )._get_combination_info()
        self.assertEqual(
            combination_info["free_qty"],
            40,
        )
        self.picking_out.action_confirm()
        self.picking_in.action_assign()
        combination_info = product_tmpl.with_context(
            website_sale_stock_get_quantity=True,
        )._get_combination_info()
        self.assertEqual(
            combination_info["free_qty"], self.product.immediately_usable_qty
        )

    def test_compute_quantities_dict_multi_product_batch(self):
        product_b = self.env["product.product"].create(
            {"name": "Storable product B", "type": "product"}
        )
        product_c = self.env["product.product"].create(
            {"name": "Storable product C", "type": "product"}
        )
        self.env["stock.quant"].create(
            {
                "product_id": product_b.id,
                "location_id": self.stock_location.id,
                "quantity": 20.0,
            }
        )
        self.env["stock.quant"].create(
            {
                "product_id": product_c.id,
                "location_id": self.stock_location.id,
                "quantity": 30.0,
            }
        )
        products = self.product | product_b | product_c
        product_product = type(self.env["product.product"])
        with patch.object(
            product_product,
            "_compute_available_quantities",
            autospec=True,
            side_effect=product_product._compute_available_quantities,
        ) as spy:
            result = products.with_context(
                website_sale_stock_available=True,
            )._compute_quantities_dict(None, None, None)
        self.assertEqual(spy.call_count, 1)
        self.assertEqual(len(result), 3)
        self.assertEqual(
            result[self.product.id]["free_qty"], self.product.immediately_usable_qty
        )
        self.assertEqual(
            result[product_b.id]["free_qty"], product_b.immediately_usable_qty
        )
        self.assertEqual(
            result[product_c.id]["free_qty"], product_c.immediately_usable_qty
        )
        free_qtys = {result[p.id]["free_qty"] for p in products}
        self.assertEqual(len(free_qtys), 3)
