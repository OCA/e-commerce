# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged("post_install", "-at_install")
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
        self.product2 = self.env["product.template"].create(
            {
                "name": "Test Product 2",
                "is_published": True,
                "website_sequence": 2,
                "type": "consu",
            }
        )

        # Configuración adicional para tests unitarios
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
            }
        )

        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
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
                "website_availability": "no_restriction",
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

    def test_04_ui_no_restriction_no_show(self):
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
        self.env["ir.filters"].create(
            {
                "name": "Test Assortment 2",
                "model_id": "product.product",
                "is_assortment": True,
                "domain": [("id", "!=", self.product2.product_variant_id.id)],
                "partner_domain": "[('id', '=', %s)]"
                % self.env.ref("base.partner_admin").id,
                "website_availability": "no_restriction",
            }
        )
        self.start_tour(
            "/shop", "test_assortment_with_no_restriction_no_show", login="admin"
        )

    def test_05_ui_cart_update_restricted_product(self):
        product_patch_path = (
            "odoo.addons.website_sale_product_assortment.models.product_product."
            "ProductProduct._show_quick_add_accesory_assortments"
        )
        with patch(product_patch_path, return_value=False):
            with self.assertRaises(UserError) as cm:
                self.sale_order._cart_update(
                    product_id=self.product.product_variant_id.id,
                    add_qty=1,
                    set_qty=1,
                )
            self.assertIn(
                "It cannot be added to the cart because the product is restricted.",
                str(cm.exception),
            )

    def test_06_ui_cart_update_allowed_product(self):
        product_patch_path = (
            "odoo.addons.website_sale_product_assortment.models.product_product."
            "ProductProduct._show_quick_add_accesory_assortments"
        )
        with patch(product_patch_path, return_value=True):
            result = self.sale_order._cart_update(
                product_id=self.product.product_variant_id.id, add_qty=1
            )
            self.assertIsInstance(result, dict)
