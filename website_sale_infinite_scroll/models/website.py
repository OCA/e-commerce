import base64

from odoo import fields, models, tools
from odoo.modules.module import get_resource_path


class Website(models.Model):
    _inherit = "website"

    def _default_preloader(self):
        img_path = get_resource_path("web", "static/src/img/throbber-large.gif")
        with tools.file_open(img_path, "rb") as f:
            return base64.b64encode(f.read())

    infinite_scroll_preloader = fields.Image(
        max_width=170,
        max_height=170,
        string="eCommerce Infinite Scroll",
        default=_default_preloader,
    )
    infinite_scroll_ppg = fields.Integer(default=24)
