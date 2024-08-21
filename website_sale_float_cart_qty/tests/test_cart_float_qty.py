import random

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestSaleOrderInherit(TransactionCase):
    def setUp(self):
        super().setUp()
        # Setup a sale order in draft state

        self.website = self.env["website"].create(
            {
                "name": "Test Website",
            }
        )

        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",  # assuming 'consu' type is allowed to add to cart
                "list_price": 100.0,
            }
        )

        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "website_id": self.website.id,
            }
        )

        self.sale_order_line = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "price_unit": self.product.list_price,
            }
        )

    def test_cart_update_add_product(self):
        """Test that a product can be added to the cart"""
        # Adding quantity to the product
        result = self.sale_order._cart_update(product_id=self.product.id, add_qty=2)

        self.assertEqual(
            result["quantity"], 3, "Product quantity should be updated to 3"
        )
        self.assertEqual(
            self.sale_order.cart_quantity, 3, "Cart quantity should be updated to 3"
        )

    def test_cart_update_add_float_product(self):
        """Test that a float quantity can be added to the cart"""
        # Adding float quantity to the product
        result = self.sale_order._cart_update(
            product_id=self.product.id, add_qty=2.2, set_qty=False
        )

        self.assertEqual(
            result["quantity"], 3.2, "Product quantity should be updated to 3.2"
        )
        self.assertEqual(
            self.sale_order.cart_quantity, 3.2, "Cart quantity should be updated to 3.2"
        )

    def test_cart_update_set_quantity(self):
        """Test that setting the quantity works"""
        # Setting quantity of the product
        result = self.sale_order._cart_update(product_id=self.product.id, set_qty=5)

        self.assertEqual(result["quantity"], 5, "Product quantity should be set to 5")
        self.assertEqual(
            self.sale_order.cart_quantity, 5, "Cart quantity should be updated to 5"
        )

    def test_cart_update_set_float_quantity(self):
        """Test that setting float quantity works"""
        # Setting float quantity of the product
        result = self.sale_order._cart_update(
            product_id=self.product.id, set_qty=9.95, add_qty=None
        )

        self.assertEqual(
            result["quantity"], 9.95, "Product quantity should be set to 9.95"
        )
        self.sale_order.cart_quantity = round(self.sale_order.cart_quantity, 9)

        self.assertEqual(
            self.sale_order.cart_quantity,
            9.95,
            "Cart quantity should be updated to 9.95",
        )

    def test_cart_update_remove_product(self):
        """Test that removing a product works"""
        # Removing the product by setting quantity to 0
        result = self.sale_order._cart_update(
            product_id=self.product.id, set_qty=0, add_qty=None
        )

        self.assertEqual(result["quantity"], 0, "Product quantity should be 0")
        self.assertEqual(self.sale_order.cart_quantity, 0, "Cart should be empty")

    def _generate_non_existent_product_id(self):
        """Generate a non-existent product ID."""
        while True:
            random_id = random.randint(1, 9999999)  # Generate a random product ID
            product = self.env["product.product"].browse(random_id)
            if not product.exists():
                return random_id

    def test_cart_update_non_existent_product(self):
        """Test that updating the cart with a non-existent product raises an error"""
        # Generate a random non-existent product ID
        non_existent_product_id = self._generate_non_existent_product_id()

        # Check if product exists in the database
        product = self.env["product.product"].browse(non_existent_product_id)
        self.assertFalse(product.exists(), "Product should not exist in the database")

        # Try updating the cart with a non-existent product
        with self.assertRaises(
            UserError, msg="Should raise UserError for non-existent product"
        ):
            self.sale_order._cart_update(product_id=non_existent_product_id, add_qty=1)

    def test_cart_update_zero_price_product(self):
        """Test that adding a zero-price product raises an error"""
        zero_price_product = self.env["product.product"].create(
            {
                "name": "Zero Price Product",
                "type": "consu",
                "list_price": 0.0,
                "detailed_type": "consu",
            }
        )

        self.sale_order.website_id.prevent_zero_price_sale = True

        with self.assertRaises(
            UserError, msg="Should raise UserError for zero-price product"
        ):
            self.sale_order._cart_update(product_id=zero_price_product.id, add_qty=1)

    def test_cart_update_without_line_id(self):
        """Test the _cart_update method when line_id is False."""
        # Call the _cart_update method with line_id set to False
        # This should trigger the else branch and use the empty order line.
        result = self.sale_order._cart_update(
            product_id=self.product.id,
            line_id=False,
            add_qty=1,
            set_qty=False,
        )

        #  that an empty sale.order.line is returned as there should be no matching line.
        self.assertNotEqual(
            result.get("line_id"),
            False,
            "line_id should not be False as it represents an empty recordset",
        )
