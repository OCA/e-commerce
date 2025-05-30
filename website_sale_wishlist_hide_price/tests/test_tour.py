# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
# Copyright 2024 Tecnativa - Pilar Vargas

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleProductAttachmentTourl(HttpCase):
    def setUp(self):
        super().setUp()
        product = self.env.ref("product.product_product_4_product_template")
        product.website_hide_price = True
        # Ensure that the product used in the tour has no optional products
        # to prevent the tour from failing
        # when the module website_sale_product_configurator is installed,
        # because this module displays a popup before adding the product to the cart
        if self.env["ir.module.module"].search(
            [
                ("name", "=", "website_sale_product_configurator"),
                ("state", "=", "installed"),
            ]
        ):
            product.optional_product_ids = [(6, 0, [])]

    def test_tour(self):
        self.start_tour("/shop", "website_sale_wishlist_hide_price_tour", login="demo")
