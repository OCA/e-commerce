from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    website_sale_infinite_scroll_preloader = fields.Image(
        related="website_id.infinite_scroll_preloader",
        readonly=False,
    )
