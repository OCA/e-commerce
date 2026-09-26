# Copyright 2026 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.website_sale.tests.common import MockRequest

from ..controllers.cart import WebsiteSaleUomContinuousCart
from .common import WebsiteSaleUomContinuousCommon


@tagged("post_install", "-at_install")
class TestCart(WebsiteSaleUomContinuousCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.controller = WebsiteSaleUomContinuousCart()

    def _add_to_cart(self, product, quantity):
        return self.controller.add_to_cart(
            product_template_id=product.product_tmpl_id.id,
            product_id=product.id,
            quantity=quantity,
        )

    def test_add_to_cart_continuous_uom(self):
        """Adding a product sold in kg keeps the decimals of the quantity.

        Scenario:
            1. Add 2.5 kg of a product to the cart.
            2. Add 1.1 kg more of the same product.
        Expected:
            - The cart line holds 2.5 kg, then 3.6 kg.
            - The added quantity is 1.1 kg, without floating point noise.
        """
        with MockRequest(self.env, website=self.website) as request:
            self._add_to_cart(self.product_kg, 2.5)
            line = request.cart.order_line
            self.assertEqual(line.product_uom_qty, 2.5)
            values = self._add_to_cart(self.product_kg, 1.1)
            self.assertEqual(line.product_uom_qty, 3.6)
            added_qty = values["notification_info"]["lines"][0]["quantity"]
            self.assertEqual(added_qty, 1.1)

    def test_update_cart_continuous_uom(self):
        """Updating a line in kg keeps the decimals allowed by the UoM precision.

        Scenario:
            1. Add a product sold in kg to the cart.
            2. Change its quantity to 7.555.
            3. Change its quantity to 1.5, giving the product instead of the line.
        Expected:
            - The cart line holds 7.56 kg (2 decimals), then 1.5 kg.
        """
        with MockRequest(self.env, website=self.website) as request:
            self._add_to_cart(self.product_kg, 1)
            line = request.cart.order_line
            values = self.controller.update_cart(line.id, 7.555)
            self.assertEqual(line.product_uom_qty, 7.56)
            self.assertEqual(values["quantity"], 7.56)
            self.controller.update_cart(False, 1.5, product_id=self.product_kg.id)
            self.assertEqual(line.product_uom_qty, 1.5)

    def test_units_integer_quantity(self):
        """Products sold in units keep integer quantities.

        Scenario:
            1. Add 2.5 units of a product to the cart.
            2. Change its quantity to 3.7.
        Expected:
            - The cart line holds 2 units, then 3 units.
        """
        with MockRequest(self.env, website=self.website) as request:
            self._add_to_cart(self.product, 2.5)
            line = request.cart.order_line
            self.assertEqual(line.product_uom_qty, 2)
            self.controller.update_cart(line.id, 3.7)
            self.assertEqual(line.product_uom_qty, 3)

    def test_cart_quantity(self):
        """The cart quantity counts each line in kg as one item, and sums the others.

        Scenario:
            1. Add 0.5 kg of a product to the cart.
            2. Add 3 units of another product.
        Expected:
            - The cart quantity is 1, then 4.
        """
        with MockRequest(self.env, website=self.website) as request:
            self._add_to_cart(self.product_kg, 0.5)
            self.assertEqual(request.cart.cart_quantity, 1)
            self._add_to_cart(self.product, 3)
            self.assertEqual(request.cart.cart_quantity, 4)
