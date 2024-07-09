# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta

from odoo.tests.common import Form, HttpCase, tagged


@tagged("post_install", "-at_install")
class WebsiteSaleStockProvisioningDate(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product = cls.env["product.product"].create(
            {
                "name": "product test - provisioning date",
                "type": "product",
                "website_published": True,
                "show_next_provisioning_date": True,
            }
        )
        incoming_picking_type = cls.env["stock.picking.type"].search(
            [
                ("code", "=", "incoming"),
                "|",
                ("warehouse_id.company_id", "=", cls.env.user.company_id.id),
                ("warehouse_id", "=", False),
            ],
            limit=1,
        )
        picking_form = Form(
            cls.env["stock.picking"].with_context(
                default_picking_type_id=incoming_picking_type.id
            ),
            view="stock.view_picking_form",
        )
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = product
            move.product_uom_qty = 10
        picking = picking_form.save()
        picking_form = Form(picking)
        picking_form.scheduled_date = datetime.now() + timedelta(days=2)
        picking = picking_form.save()
        picking.action_confirm()

        cls.warehouse_1 = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)]
        )
        # Create two stockable products
        cls.product_A = cls.env["product.product"].create(
            {
                "name": "Product A",
                "allow_out_of_stock_order": False,
                "type": "product",
                "default_code": "E-COM1",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Partner", "email": "prueba@pruebae.es"}
        )
        # Add 10 Product A in WH1 and 15 Product 1 in WH2
        quants = (
            cls.env["stock.quant"]
            .with_context(inventory_mode=True)
            .create(
                [
                    {
                        "product_id": cls.product_A.id,
                        "inventory_quantity": 10.0,
                        "location_id": cls.warehouse_1.lot_stock_id.id,
                    }
                ]
            )
        )
        quants.action_apply_inventory()
        sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_A.id,
                            "product_uom_qty": 3,
                        },
                    )
                ],
            }
        )
        sale.action_confirm()

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour(
            "/shop",
            "website_sale_stock_provisioning_date",
            login="admin",
        )

    def test_search_qty_free(self):
        templates = self.env["product.template"].search(
            [("free_qty", ">", 0), ("id", "=", self.product_A.product_tmpl_id.id)]
        )
        self.assertEqual(templates.free_qty, 7)
