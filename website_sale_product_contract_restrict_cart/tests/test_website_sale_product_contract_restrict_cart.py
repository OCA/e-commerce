# Copyright 2023 Onestein - Anjeel Haria
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.website.tools import MockRequest
from odoo.addons.website_sale.controllers.main import WebsiteSale


@tagged("post_install", "-at_install")
class WebsiteSaleCart(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(WebsiteSaleCart, cls).setUpClass()
        cls.website = cls.env["website"].browse(1)
        cls.WebsiteSaleController = WebsiteSale()
        cls.contract = cls.env["contract.template"].create({"name": "Test"})
        # Create two contract products
        cls.product_A = cls.env["product.product"].create(
            {
                "name": "Product A",
                "sale_ok": True,
                "website_published": True,
                "is_contract": True,
                "type": "service",
                "property_contract_template_id": cls.contract.id,
            }
        )

        cls.product_B = cls.env["product.product"].create(
            {
                "name": "Product B",
                "sale_ok": True,
                "website_published": True,
                "is_contract": True,
                "type": "service",
                "property_contract_template_id": cls.contract.id,
            }
        )
        # Create Non contract product
        cls.product_C = cls.env["product.product"].create(
            {
                "name": "Product B",
                "sale_ok": True,
                "website_published": True,
            }
        )

    def test_add_cart_contract_product_with_multiple_quantity(self):
        """When the users try to add contract product with quantity more than 1 to
        their cart , a warning should be returned and the quantity updated to 0."""
        with MockRequest(self.env, website=self.website):
            values = self.WebsiteSaleController.cart_update_json(
                product_id=self.product_A.id, add_qty=2
            )
            self.assertTrue(values.get("warning", False))
            self.assertEqual(values.get("quantity"), 1)

    def test_add_contract_product_to_cart_with_other_contract_product(self):
        """When the users try to add more than one different contract products to
        their cart , a warning should be returned and the quantity updated to 0."""
        with MockRequest(self.env, website=self.website):
            self.WebsiteSaleController.cart_update_json(
                product_id=self.product_A.id, add_qty=1
            )
            values = self.WebsiteSaleController.cart_update_json(
                product_id=self.product_B.id, add_qty=1
            )
            self.assertTrue(values.get("warning", False))
            self.assertEqual(values.get("quantity"), 0)
            sale_order = self.website.sale_get_order()
            # Only one order line would be there in the cart
            self.assertEqual(len(sale_order.order_line), 1)

    def test_add_non_contract_product_to_cart_with_contract_product(self):
        """When the users try to add non contract products to their cart which
        already has contract products,a warning should be returned and the quantity
        updated to 0."""
        with MockRequest(self.env, website=self.website):
            self.WebsiteSaleController.cart_update_json(
                product_id=self.product_A.id, add_qty=1
            )
            values = self.WebsiteSaleController.cart_update_json(
                product_id=self.product_C.id, add_qty=1
            )
            self.assertTrue(values.get("warning", False))
            self.assertEqual(values.get("quantity"), 0)
            sale_order = self.website.sale_get_order()
            # Only one order line would be there in the cart
            self.assertEqual(len(sale_order.order_line), 1)

    def test_add_contract_product_to_cart_with_non_contract_product(self):
        """When the users try to add contract products to their cart which already has
        non contract products,a warning should be returned and the quantity updated
        to 1."""
        with MockRequest(self.env, website=self.website):
            self.WebsiteSaleController.cart_update_json(
                product_id=self.product_C.id, add_qty=1
            )
            values = self.WebsiteSaleController.cart_update_json(
                product_id=self.product_A.id, add_qty=1
            )
            self.assertTrue(values.get("warning", False))
            self.assertEqual(values.get("quantity"), 1)
            sale_order = self.website.sale_get_order()
            # Only one order line would be there in the cart
            self.assertEqual(len(sale_order.order_line), 1)

    def test_add_contract_product_with_multiple_qty_to_cart_with_non_contract_product(
        self,
    ):
        """When the users try to add contract products with more than 1 quantity to
        their cart which already has non contract products,a warning should be returned
         and the quantity updated to 1."""
        with MockRequest(self.env, website=self.website):
            self.WebsiteSaleController.cart_update_json(
                product_id=self.product_C.id, add_qty=1
            )
            values = self.WebsiteSaleController.cart_update_json(
                product_id=self.product_A.id, add_qty=2
            )
            self.assertTrue(values.get("warning", False))
            self.assertEqual(values.get("quantity"), 1)
            sale_order = self.website.sale_get_order()
            # Only one order line would be there in the cart
            self.assertEqual(len(sale_order.order_line), 1)
