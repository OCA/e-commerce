# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
# Copyright 2024 Tecnativa - Pilar Vargas

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleProductAttachmentTourl(HttpCase):
    def setUp(self):
        super().setUp()
        product = self.env.ref("product.product_product_4_product_template")
        product.website_hide_price = True

    def test_tour(self):
        self.start_tour("/shop", "website_sale_wishlist_hide_price_tour", login="demo")
