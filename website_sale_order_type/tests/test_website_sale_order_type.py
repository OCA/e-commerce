# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import HttpCase, RecordCapturer, tagged


@tagged("post_install", "-at_install")
class TestFrontend(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_type_model = cls.env["sale.order.type"]
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "Test Product SO Type",
                "is_published": True,
                "website_sequence": 1,
                "type": "consu",
            }
        )
        cls.partner = cls.env.ref("base.partner_admin")
        cls.sale_pricelist = cls.env["product.pricelist"].create(
            {"name": "Test Pricelist"}
        )
        cls.sale_type = cls.create_sale_type()

    @classmethod
    def create_sale_type(cls):
        cls.sequence = cls.env["ir.sequence"].create(
            {
                "name": "Test Sales Order",
                "code": "sale.order",
                "prefix": "TSO",
                "padding": 3,
            }
        )
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.immediate_payment = cls.env.ref("account.account_payment_term_immediate")
        cls.free_carrier = cls.env.ref("account.incoterm_FCA")
        return cls.sale_type_model.create(
            {
                "name": "Test Sale Order Type",
                "sequence_id": cls.sequence.id,
                "journal_id": cls.journal.id,
                "warehouse_id": cls.warehouse.id,
                "picking_policy": "one",
                "payment_term_id": cls.immediate_payment.id,
                "pricelist_id": cls.sale_pricelist.id,
                "incoterm_id": cls.free_carrier.id,
            }
        )

    def test_website_sale_order_type(self):
        self.partner.sale_type = self.sale_type
        # In frontend, create an order
        with RecordCapturer(self.env["sale.order"], []) as capture:
            self.start_tour("/shop", "website_sale_order_type_tour", login="admin")
        # Verify the followers of mail.message
        created_order = capture.records
        self.assertEqual(created_order.type_id, self.sale_type)
        self.assertEqual(created_order.payment_term_id, self.sale_type.payment_term_id)
        self.assertEqual(created_order.pricelist_id, self.sale_type.pricelist_id)
