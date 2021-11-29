# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase


class TestUI(HttpCase):
    def setUp(self):
        super().setUp()
        self.product = self.env["product.template"].create(
            {
                "name": "Test Product 1",
                "is_published": True,
                "website_sequence": 1,
                "type": "consu",
            }
        )

    def test_01_ui_no_restriction(self):
        self.env["ir.filters"].create(
            {
                "name": "Test Assortment",
                "model_id": "product.product",
                "is_assortment": True,
                "domain": [("id", "!=", self.product.product_variant_id.id)],
                "partner_domain": "[('id', '=', %s)]"
                % self.env.ref("base.partner_admin").id,
            }
        )
        self.start_tour("/shop", "test_assortment_with_no_restriction", login="admin")

    def test_02_ui_no_show(self):
        self.env["ir.filters"].create(
            {
                "name": "Test Assortment",
                "model_id": "product.product",
                "is_assortment": True,
                "domain": [("id", "!=", self.product.product_variant_id.id)],
                "partner_domain": "[('id', '=', %s)]"
                % self.env.ref("base.partner_admin").id,
                "website_availability": "no_show",
            }
        )
        self.start_tour("/shop", "test_assortment_with_no_show", login="admin")

    def test_03_ui_no_purchase(self):
        self.env["ir.filters"].create(
            {
                "name": "Test Assortment",
                "model_id": "product.product",
                "is_assortment": True,
                "domain": [("id", "!=", self.product.product_variant_id.id)],
                "partner_domain": "[('id', '=', %s)]"
                % self.env.ref("base.partner_admin").id,
                "website_availability": "no_purchase",
                "message_unavailable": "Can't purchase",
                "assortment_information": """<span name='testing'>
                        This product is not available for purchase
                    </span>
                """,
            }
        )
        self.start_tour("/shop", "test_assortment_with_no_purchase", login="admin")
