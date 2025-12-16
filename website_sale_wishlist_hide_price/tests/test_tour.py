# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
# Copyright 2024 Tecnativa - Pilar Vargas

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleProductAttachmentTourl(HttpCase):
    def setUp(self):
        super().setUp()
        product = self.env["product.product"].create(
            {"name": "Test Product", "is_published": True}
        )
        product.website_hide_price = True
        self.env["res.users"].create(
            {
                "name": "Wishlist Hide Price User",
                "login": "wishlist_hide_price_user",
                "email": "wishlist_hide_price_user@example.com",
            }
        )

    def test_tour(self):
        self.start_tour(
            "/shop",
            "website_sale_wishlist_hide_price_tour",
            login="wishlist_hide_price_user",
            debug=True,
        )
