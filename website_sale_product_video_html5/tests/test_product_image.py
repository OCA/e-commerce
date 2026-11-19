# Copyright 2026 Bosd
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import io

from PIL import Image

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged
from odoo.tools import mute_logger

from ..tools import (
    ALLOWED_HOSTS_PARAM,
    get_allowed_hosts,
    get_html5_video_mimetype,
    is_html5_video_url,
    split_video_url,
)

CDN_URL = "https://res.cloudinary.com/demo/video/upload/f_auto:video,q_auto/v1/abc"


def _image_b64():
    buffer = io.BytesIO()
    Image.new("RGB", (16, 16), "purple").save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue())


@tagged("post_install", "-at_install")
class TestProductImage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env["product.template"].create({"name": "Forklift"})

    def _create_image(self, video_url, **vals):
        return self.env["product.image"].create(
            {
                "name": "Demo",
                "product_tmpl_id": self.template.id,
                "video_url": video_url,
                **vals,
            }
        )

    def test_video_file(self):
        image = self._create_image("https://cdn.example.com/videos/demo.mp4")
        self.assertEqual(
            image.embed_code,
            '<video class="o_product_video_html5 w-100 h-100" '
            'src="https://cdn.example.com/videos/demo.mp4" '
            'playsinline="playsinline" preload="none" controls="controls"></video>',
        )

    def test_video_options(self):
        image = self._create_image(
            "https://cdn.example.com/demo.webm?sig=a%2Fb&autoplay=1&loop=1&controls=0"
        )
        self.assertIn(
            'src="https://cdn.example.com/demo.webm?sig=a%2Fb"', image.embed_code
        )
        self.assertIn('autoplay="autoplay" muted="muted"', image.embed_code)
        self.assertIn('preload="auto"', image.embed_code)
        self.assertIn('loop="loop"', image.embed_code)
        self.assertNotIn("controls", image.embed_code)

    def test_poster(self):
        image = self._create_image(
            "https://cdn.example.com/demo.mp4", image_1920=_image_b64()
        )
        self.assertIn(
            f'poster="/web/image/product.image/{image.id}/image_1024?unique=',
            image.embed_code,
        )
        website = self.env["website"].get_current_website()
        website.write(
            {
                "cdn_activated": True,
                "cdn_url": "https://images.example.com",
                "cdn_filters": "^/web/image",
            }
        )
        image.invalidate_recordset(["embed_code"])
        self.assertIn(
            f'poster="https://images.example.com/web/image/product.image/{image.id}/',
            image.embed_code,
        )

    def test_escaping(self):
        image = self._create_image('https://cdn.example.com/a.mp4?x="><script>')
        self.assertNotIn("<script>", image.embed_code)
        self.assertIn("&#34;&gt;&lt;script&gt;", image.embed_code)

    # Odoo cannot find the language of its error message outside of requests.
    @mute_logger("odoo.tools.translate")
    def test_allowed_host(self):
        with self.assertRaises(ValidationError):
            self._create_image(CDN_URL)
        self.env["ir.config_parameter"].set_param(
            ALLOWED_HOSTS_PARAM, "res.cloudinary.com"
        )
        image = self._create_image(CDN_URL)
        self.assertIn(f'src="{CDN_URL}"', image.embed_code)

    def test_other_platforms_unchanged(self):
        self.env["ir.config_parameter"].set_param(ALLOWED_HOSTS_PARAM, "youtu.be")
        image = self._create_image("https://youtu.be/nbso3NVz3p8")
        self.assertIn("<iframe", image.embed_code)
        self.assertIn("youtube.com/embed/nbso3NVz3p8", image.embed_code)

    @mute_logger("odoo.tools.translate")
    def test_invalid_url(self):
        with self.assertRaises(ValidationError):
            self._create_image("https://www.example.com/page.html")

    def test_no_video(self):
        image = self._create_image(False, image_1920=_image_b64())
        self.assertFalse(image.embed_code)

    def test_settings(self):
        self.env["res.config.settings"].create(
            {"product_video_allowed_hosts": "res.cloudinary.com"}
        ).execute()
        self.assertEqual(get_allowed_hosts(self.env), ["res.cloudinary.com"])


@tagged("post_install", "-at_install")
class TestTools(TransactionCase):
    def test_is_html5_video_url(self):
        self.assertTrue(is_html5_video_url("//cdn.example.com/a.M4V#t=3"))
        self.assertTrue(is_html5_video_url(CDN_URL, ["res.cloudinary.com"]))
        self.assertTrue(
            is_html5_video_url(
                "https://eu.res.cloudinary.com/x", ["res.cloudinary.com"]
            )
        )
        for url in (
            "",
            "cdn.example.com/a.mp4",
            "ftp://cdn.example.com/a.mp4",
            "https://cdn.example.com/a.mp4.html",
            "https://res.cloudinary.com.evil.com/x",
        ):
            with self.subTest(url=url):
                self.assertFalse(is_html5_video_url(url, ["res.cloudinary.com"]))

    def test_mimetype(self):
        self.assertEqual(get_html5_video_mimetype("https://x.org/a.ogv"), "video/ogg")
        self.assertIsNone(get_html5_video_mimetype(CDN_URL))

    def test_split_video_url(self):
        self.assertEqual(
            split_video_url("https://x.org/a.mp4?autoplay=0&loop=1#t=5"),
            ("https://x.org/a.mp4?autoplay=0#t=5", {"loop": True}),
        )
        self.assertEqual(
            split_video_url("https://x.org/a.mp4"), ("https://x.org/a.mp4", {})
        )
