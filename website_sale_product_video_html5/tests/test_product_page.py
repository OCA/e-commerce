# Copyright 2026 Bosd
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged

from .test_product_image import _image_b64


@tagged("post_install", "-at_install")
class TestProductPage(HttpCase):
    def test_product_page_video(self):
        template = self.env["product.template"].create(
            {
                "name": "Forklift with video",
                "is_published": True,
                "sale_ok": True,
                "website_id": self.env["website"].get_current_website().id,
                "image_1920": _image_b64(),
                "product_template_image_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Demo",
                            "video_url": "https://cdn.example.com/videos/demo.mp4",
                            "image_1920": _image_b64(),
                        },
                    )
                ],
            }
        )
        response = self.url_open(template.website_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            '<video class="o_product_video_html5 w-100 h-100" '
            'src="https://cdn.example.com/videos/demo.mp4"',
            response.text,
        )
