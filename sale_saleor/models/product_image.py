# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.image import is_image_size_above

from odoo.addons.web_editor.tools import get_video_embed_code, get_video_thumbnail

from ..helpers import get_active_saleor_account

_logger = logging.getLogger(__name__)


class ProductImage(models.Model):
    _name = "saleor.product.image"
    _description = "Product Image"
    _inherit = ["image.mixin"]
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    image_1920 = fields.Image()
    product_tmpl_id = fields.Many2one(
        string="Product Template",
        comodel_name="product.template",
        ondelete="cascade",
        index=True,
        required=True,
    )
    video_url = fields.Char(
        string="Video URL",
        help="URL of a video for showcasing your product.",
    )
    embed_code = fields.Html(compute="_compute_embed_code", sanitize=False)
    can_image_1024_be_zoomed = fields.Boolean(
        string="Can Image 1024 be zoomed",
        compute="_compute_can_image_1024_be_zoomed",
        store=True,
    )
    saleor_image_id = fields.Char(
        string="Saleor Image ID",
        copy=False,
        index=True,
        help="ID of this image in Saleor",
    )

    @api.depends("image_1920")
    def _compute_can_image_1024_be_zoomed(self):
        for image in self:
            image.can_image_1024_be_zoomed = image.image_1920 and is_image_size_above(
                image.image_1920, image.image_1024
            )

    @api.depends("video_url")
    def _compute_embed_code(self):
        for image in self:
            if image.video_url:
                image.embed_code = get_video_embed_code(image.video_url)
            else:
                image.embed_code = False

    def unlink(self):
        """
        Override unlink to delete corresponding image from Saleor
        when an image is deleted in Odoo.
        """
        account = get_active_saleor_account(self.env)

        # Delete images from Saleor if they exist
        for image in self.filtered("saleor_image_id"):
            try:
                client = account._get_client()
                account._delete_product_image(client, image.saleor_image_id)
            except Exception as e:
                _logger.error(
                    "Failed to delete image %s from Saleor: %s",
                    image.saleor_image_id,
                    str(e),
                    exc_info=True,
                )

        # Call the original unlink method
        return super().unlink()

    @api.onchange("video_url")
    def _onchange_video_url(self):
        if not self.image_1920:
            thumbnail = get_video_thumbnail(self.video_url)
            self.image_1920 = thumbnail and base64.b64encode(thumbnail) or False

    @api.constrains("video_url")
    def _check_valid_video_url(self):
        for image in self:
            if image.video_url and not image.embed_code:
                raise ValidationError(
                    _(
                        "Provided video URL for %s is not valid."
                        " Please enter a valid video URL.",
                        image.name,
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        """
        Create product images with the provided values.
        Ensures product_tmpl_id is set either from context or values.
        """
        for vals in vals_list:
            if (
                "product_tmpl_id" not in vals
                and "default_product_tmpl_id" in self.env.context
            ):
                vals["product_tmpl_id"] = self.env.context["default_product_tmpl_id"]
        return super().create(vals_list)
