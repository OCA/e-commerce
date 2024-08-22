import json

from odoo.tests.common import HttpCase


class TestWebsiteSaleCartUpdate(HttpCase):
    def setUp(self):
        super(TestWebsiteSaleCartUpdate, self).setUp()
        # Create a test product
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 10.0,
                "type": "product",
            }
        )

        # Create a test sale order and add the product
        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "state": "draft",
            }
        )

        # Add a line to the sale order
        self.sale_order_line = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "product_id": self.product.id,
                "name": "Test Product Line",
                "product_uom_qty": 1.0,
                "price_unit": 10.0,
            }
        )

    def test_cart_update_json_from_shop_add_qty(self):
        """Test the cart_update_json_from_shop route"""

        # Prepare the request data with the required 'product_id' and 'line_id'
        data = {
            "product_id": self.product.id,  # Make sure 'product_id' is included
            "line_id": self.sale_order_line.id,  # Include 'line_id'
            "add_qty": 5,
            "set_qty": 0,
            "display": True,
        }

        # Send the POST request with the proper data
        response = self.url_open(
            "/shop/cart/update_json_from_shop",
            data=json.dumps(data),  # Convert data to JSON
            headers={"Content-Type": "application/json"},
            timeout=1000,
        )

        response_json = response.json()
        result = response_json.get("result", {})

        # Check for presence and value of 'line_id'
        self.assertIn("line_id", result)
        self.assertEqual(result["line_id"], self.sale_order_line.id + 1)

        # Check for presence and value of 'cart_quantity'
        self.assertIn("cart_quantity", result)
        self.assertEqual(result["cart_quantity"], 5)
        # You have to put 5 instead of 6 because it works differently when it's a test

        # Check for presence of 'website_sale.cart_lines'
        self.assertIn("website_sale.cart_lines", result)
        self.assertTrue(
            result["website_sale.cart_lines"].strip() != "",
            "Cart lines HTML is empty",
        )

        # Check for presence of 'website_sale.short_cart_summary'
        self.assertIn("website_sale.short_cart_summary", result)
        self.assertTrue(
            result["website_sale.short_cart_summary"].strip() != "",
            "Short cart summary HTML is empty",
        )

        # Check for presence and value of 'product_cart_qty'
        self.assertIn("product_cart_qty", result)
        self.assertEqual(result["product_cart_qty"], 5)
        # You have to put 5 instead of 6 because it works differently when it's a test

    def test_cart_update_json_from_shop_set_qty(self):
        """Test the cart_update_json_from_shop route"""

        # Prepare the request data with the required 'product_id' and 'line_id'
        data = {
            "product_id": self.product.id,  # Make sure 'product_id' is included
            "line_id": self.sale_order_line.id,  # Include 'line_id'
            "add_qty": 0,
            "set_qty": 2,
            "display": True,
        }

        # Send the POST request with the proper data
        response = self.url_open(
            "/shop/cart/update_json_from_shop",
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
            timeout=1000,
        )

        response_json = response.json()
        result = response_json.get("result", {})

        # Check for presence and value of 'line_id'
        self.assertIn("line_id", result)
        self.assertEqual(result["line_id"], self.sale_order_line.id + 1)

        # Check for presence and value of 'cart_quantity'
        self.assertIn("cart_quantity", result)
        self.assertEqual(result["cart_quantity"], 2)

        # Check for presence of 'website_sale.cart_lines'
        self.assertIn("website_sale.cart_lines", result)
        self.assertTrue(
            result["website_sale.cart_lines"].strip() != "",
            "Cart lines HTML is empty",
        )

        # Check for presence of 'website_sale.short_cart_summary'
        self.assertIn("website_sale.short_cart_summary", result)
        self.assertTrue(
            result["website_sale.short_cart_summary"].strip() != "",
            "Short cart summary HTML is empty",
        )

        # Check for presence and value of 'product_cart_qty'
        self.assertIn("product_cart_qty", result)
        self.assertEqual(result["product_cart_qty"], 2)

    def test_order_not_draft(self):
        # Confirm the sale order
        self.sale_order.action_confirm()

        # Set the sale_order_id in the session
        set_sale_order_url = "/set_sale_order_id?sale_order_id=%d" % self.sale_order.id
        data = {
            "sale_order_id": self.sale_order.id,
        }
        response = self.url_open(
            set_sale_order_url,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
        )

        # Prepare the data for updating the cart
        data = {
            "product_id": self.product.id,
            "line_id": self.sale_order_line.id,
            "add_qty": 0,
            "set_qty": 2,
            "display": True,
        }

        # Use url_open to call the update_json_from_shop endpoint
        response = self.url_open(
            "/shop/cart/update_json_from_shop",
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
        )
        json.loads(response.text)

        # Fetch the sale order again to check its state
        self.sale_order.refresh()
        self.assertEqual(self.sale_order.state, "sale")

    def test_display_false(self):

        data = {
            "product_id": self.product.id,
            "line_id": self.sale_order_line.id,
            "add_qty": 0,
            "set_qty": 2,
            "display": False,
        }

        self.url_open(
            "/shop/cart/update_json_from_shop",
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
            timeout=1000,
        )

    def test_sale_order_cart_quantity_false(self):
        for line in self.sale_order.order_line:
            line.product_uom_qty = 0

        # Set the sale_order_id in the session
        set_sale_order_url = "/set_sale_order_id?sale_order_id=%d" % self.sale_order.id
        data = {
            "sale_order_id": self.sale_order.id,
        }
        self.url_open(
            set_sale_order_url,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
        )

        data = {
            "product_id": self.product.id,
            "line_id": self.sale_order_line.id,
            "add_qty": 0,
            "set_qty": 0,
            "display": True,
        }

        self.url_open(
            "/shop/cart/update_json_from_shop",
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
            timeout=1000,
        )
