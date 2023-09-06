# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
# Copyright 2021 Tecnativa - Víctor Martínez

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleProductAttachmentTourl(HttpCase):
    def test_tour(self):
        attachment = self.env.ref("website.library_image_11")
        product = self.env.ref("product.product_product_4_product_template")
        product.website_attachment_ids = [(6, 0, [attachment.id])]
        self.start_tour("/shop", "website_sale_product_attachment_tour", login="demo")
