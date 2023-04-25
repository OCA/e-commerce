from odoo.tests import TransactionCase, tagged

from odoo.addons.website.tools import MockRequest
from odoo.addons.website_sale_ajaxify_cart.controllers.main import WebsiteSaleForm


@tagged("post_install", "-at_install")
class TestWebsiteSale(TransactionCase):
    def setUp(self):
        super(TestWebsiteSale, self).setUp()
        self.WebsiteSaleFormController = WebsiteSaleForm()
        self.demo_user = self.env.ref("base.user_demo")
        self.website = self.env["website"].browse(1)
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product #1",
                "sale_ok": True,
            }
        )
        self.product_test = self.env["product.product"].create(
            {
                "name": "Test Product #2",
                "sale_ok": True,
            }
        )

    def test_cart_ajaxify_update_json(self):
        """Test flow how to add to cart dynamic"""
        with MockRequest(
            self.product.with_user(self.demo_user).env, website=self.website
        ):
            values = self.WebsiteSaleFormController.cart_ajaxify_update_json(
                self.product.id,
            )
            self.assertEqual(
                values.get("quantity", 0.0), 1, msg="Quantity count must be equal to 1"
            )
            self.assertEqual(
                values.get("cart_quantity", 0),
                1,
                msg="Cart Quantity must be equal to 1",
            )
            sol = self.env["sale.order.line"].browse(values.get("line_id"))
            order_id = sol.order_id
            order_line = order_id.order_line
            self.assertEqual(len(order_line), 1, msg="Lines count must be equal to 1")
            self.assertEqual(
                order_line.product_id,
                self.product,
                msg="SOL Product must be equal to 'Test Product #1'",
            )
            self.assertEqual(
                order_line.product_uom_qty, 1, msg="Product Qty must be equal to 1"
            )
            values = self.WebsiteSaleFormController.cart_ajaxify_update_json(
                self.product_test.id, add_qty=5
            )
            self.assertEqual(
                values.get("quantity", 0.0), 5, msg="Quantity count must be equal to 5"
            )
            self.assertEqual(
                values.get("cart_quantity", 0),
                6,
                msg="Cart Quantity must be equal to 6",
            )
            order_lines = order_id.order_line
            self.assertEqual(len(order_lines), 2, msg="Lines count must be equal to 2")
            product_sol, product_test_sol = order_lines
            self.assertEqual(
                product_sol.product_id,
                self.product,
                msg="SOL Product must be equal to 'Test Product #1'",
            )
            self.assertEqual(
                product_sol.product_uom_qty, 1, msg="Product Qty must be equal to 1"
            )
            self.assertEqual(
                product_test_sol.product_id,
                self.product_test,
                msg="SOL Product must be equal to 'Test Product #2'",
            )
            self.assertEqual(
                product_test_sol.product_uom_qty,
                5,
                msg="Product Qty must be equal to 5",
            )
            self.assertIn(
                "website_sale.cart_lines",
                values,
                msg="'website_sale.cart_lines' key contains in dict",
            )
            self.assertIn(
                "website_sale.short_cart_summary",
                values,
                msg="'website_sale.short_cart_summary' key contains in dict",
            )
            order_id.action_confirm()
            values = self.WebsiteSaleFormController.cart_ajaxify_update_json(
                self.product_test.id,
                add_qty=2,
                product_custom_attribute_values="[]",
                no_variant_attribute_values="[]",
                display=False,
            )
            self.assertEqual(
                values.get("quantity", 0.0), 2, msg="Quantity count must be equal to 2"
            )
            self.assertEqual(
                values.get("cart_quantity", 0),
                2,
                msg="Cart Quantity must be equal to 2",
            )
            self.assertNotIn(
                "website_sale.cart_lines",
                values,
                msg="'website_sale.cart_lines' key doesn't contains in dict",
            )
            self.assertNotIn(
                "website_sale.short_cart_summary",
                values,
                msg="'website_sale.short_cart_summary' key doesn't contains in dict",
            )
            sol = self.env["sale.order.line"].browse(values.get("line_id"))
            new_order_id = sol.order_id
            self.assertNotEqual(order_id, new_order_id)
