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
        cls.website = cls.env["website"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.sale_pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test Pricelist",
                "website_id": cls.website.id,
            }
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
        self.website.sale_type_id = False
        self.partner.sale_type = self.sale_type
        # In frontend, create an order
        with RecordCapturer(self.env["sale.order"], []) as capture:
            self.start_tour("/shop", "website_sale_order_type_tour", login="admin")
        # Verify the followers of mail.message
        created_order = capture.records
        self.assertEqual(created_order.type_id, self.sale_type)
        self.assertEqual(created_order.payment_term_id, self.sale_type.payment_term_id)
        if self.env["res.groups"]._is_feature_enabled(
            "product.group_product_pricelist"
        ):
            self.assertEqual(created_order.pricelist_id, self.sale_type.pricelist_id)
        else:
            self.assertFalse(created_order.pricelist_id)

    def test_get_pricelist_available_filtered_by_sale_type(self):
        if not self.env["res.groups"]._is_feature_enabled(
            "product.group_product_pricelist"
        ):
            self.skipTest("Pricelist feature is disabled.")
        self.website.sale_type_id = False
        self.partner.sale_type = self.sale_type
        admin = self.env.ref("base.user_admin")
        website = self.env["website"].get_current_website().with_user(admin)

        pricelists = website.get_pricelist_available()

        self.assertEqual(pricelists, self.sale_type.pricelist_id)

    def test_website_sale_type(self):
        self.partner.sale_type = False
        self.website.sale_type_id = self.sale_type

        with RecordCapturer(self.env["sale.order"], []) as capture:
            self.start_tour("/shop", "website_sale_order_type_tour", login="admin")

        created_order = capture.records
        self.assertEqual(created_order.type_id, self.sale_type)
        self.assertEqual(created_order.payment_term_id, self.sale_type.payment_term_id)

    def test_website_sale_type_takes_precedence_over_partner_sale_type(self):
        website_sale_type = self.sale_type.copy({"name": "Website Sale Order Type"})
        partner_sale_type = self.sale_type.copy({"name": "Partner Sale Order Type"})
        self.website.sale_type_id = website_sale_type
        self.partner.sale_type = partner_sale_type

        sale_type = self.website._get_sale_order_type(self.partner)

        self.assertEqual(sale_type, website_sale_type)

    def test_get_pricelist_available_filtered_by_website_sale_type(self):
        if not self.env["res.groups"]._is_feature_enabled(
            "product.group_product_pricelist"
        ):
            self.skipTest("Pricelist feature is disabled.")
        self.partner.sale_type = False
        self.website.sale_type_id = self.sale_type
        admin = self.env.ref("base.user_admin")
        website = self.env["website"].get_current_website().with_user(admin)

        pricelists = website.get_pricelist_available()

        self.assertEqual(pricelists, self.sale_type.pricelist_id)

    def test_public_cart_creation_with_website_sale_type(self):
        self.partner.sale_type = False
        self.website.sale_type_id = self.sale_type

        with RecordCapturer(self.env["sale.order"], []) as capture:
            self.make_jsonrpc_request(
                "/shop/cart/add",
                {
                    "product_template_id": self.product_template.id,
                    "product_id": self.product_template.product_variant_id.id,
                    "quantity": 1,
                },
            )

        self.assertEqual(capture.records.type_id, self.sale_type)
