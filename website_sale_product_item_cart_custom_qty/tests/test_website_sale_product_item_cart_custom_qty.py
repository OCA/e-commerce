# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import HttpCase


class TestWebsiteSaleProductItemCartCustomQty(HttpCase):
    def setUp(self):
        super().setUp()
        products_add_to_cart = self.env["website"].viewref(
            "website_sale.products_add_to_cart", raise_if_not_found=False
        )
        always_display_qty_buttons = self.env["website"].viewref(
            "website_sale_product_item_cart_custom_qty.always_display_qty_buttons",
            raise_if_not_found=False,
        )
        self.env["product.template"].create(
            {"name": "Test Product", "is_published": True, "website_sequence": 1}
        )
        products_add_to_cart.active = True
        always_display_qty_buttons.active = True

    def test_frontend_website(self):
        """Test frontend tour."""
        self.start_tour(
            "/shop", "website_sale_product_item_cart_custom_qty", login="admin"
        )
