# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests.common import tagged

from odoo.addons.website.tools import MockRequest
from odoo.addons.website_sale.tests.test_website_sale_cart import WebsiteSaleCart
from odoo.addons.website_sale_empty_cart.controllers.main import WebsiteSaleEmptyCart


@tagged("post_install", "-at_install")
class TestWebsiteSaleEmptyCart(WebsiteSaleCart):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.WebsiteSaleControllerEmptyCart = WebsiteSaleEmptyCart()

    def test_clear_cart(self):
        website = self.website.with_user(self.public_user)
        with MockRequest(self.product.with_user(self.public_user).env, website=website):
            self.WebsiteSaleController.cart_update_json(
                product_id=self.product.id, add_qty=1
            )
            sale_order = website.sale_get_order()
            self.assertTrue(sale_order.order_line)

            self.WebsiteSaleControllerEmptyCart.cart(empty_cart=True)

            self.assertFalse(sale_order.order_line)
