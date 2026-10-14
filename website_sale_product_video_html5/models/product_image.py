# Copyright 2026 Bosd
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import api, models

from odoo.addons.html_editor.tools import get_video_source_data

from ..tools import get_allowed_hosts, is_html5_video_url, split_video_url


class ProductImage(models.Model):
    _inherit = "product.image"

    @api.depends("video_url")
    def _compute_embed_code(self):
        allowed_hosts = get_allowed_hosts(self.env)
        html5_images = self.filtered(
            lambda image: is_html5_video_url(image.video_url, allowed_hosts)
            and not get_video_source_data(image.video_url)
        )
        for image in html5_images:
            image.embed_code = image._get_html5_video_embed_code()
        return super(ProductImage, self - html5_images)._compute_embed_code()

    def _get_html5_video_poster_url(self):
        """URL of the image shown before the video is played."""
        self.ensure_one()
        if not self._origin.id or not self.with_context(bin_size=True).image_1024:
            return False
        website = self.env["website"].get_current_website()
        url = website.image_url(self._origin, "image_1024")
        if website.cdn_activated:
            url = website.get_cdn_url(url)
        return url

    def _get_html5_video_embed_code(self):
        self.ensure_one()
        src, options = split_video_url(self.video_url.strip())
        attributes = {
            "class": "o_product_video_html5 w-100 h-100",
            "src": src,
            "playsinline": "playsinline",
            # Nothing is downloaded until the visitor starts the video.
            "preload": "none",
        }
        if not options.get("hide_controls"):
            attributes["controls"] = "controls"
        if options.get("autoplay"):
            # Browsers only allow autoplay for muted videos.
            attributes.update(autoplay="autoplay", muted="muted", preload="auto")
        if options.get("loop"):
            attributes["loop"] = "loop"
        poster = self._get_html5_video_poster_url()
        if poster:
            attributes["poster"] = poster
        return Markup("<video %s></video>") % Markup(" ").join(
            Markup('%s="%s"') % item for item in attributes.items()
        )
