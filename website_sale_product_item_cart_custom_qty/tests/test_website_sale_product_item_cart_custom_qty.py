# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import HttpCase


class TestWebsiteSaleProductItemCartCustomQty(HttpCase):
    def setUp(self):
        super().setUp()
        view = self.env.ref("website_sale.products_add_to_cart")
        view.active = True
        self.env["product.template"].create(
            {"name": "Test Product", "is_published": True, "website_sequence": 1}
        )

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour(
            "/shop", "website_sale_product_item_cart_custom_qty", login="admin"
        )
