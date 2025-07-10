# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
# Copyright 2021 Tecnativa - Víctor Martínez

from odoo.tests import common


class TestWebsiteSaleProductAttachmentTourl(common.HttpCase):
    def setUp(self):
        super().setUp()
        attachment = self.env.ref("website.library_image_11")
        product = self.env.ref("product.product_product_4_product_template")
        product.website_attachment_ids = [(6, 0, [attachment.id])]
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
        self.start_tour("/shop", "website_sale_product_attachment_tour", login="demo")
