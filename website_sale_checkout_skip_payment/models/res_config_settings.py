# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    website_sale_checkout_skip_message = fields.Text(
        "Website Sale Checkout Skip Message",
        related="website_id.website_sale_checkout_skip_message",
        readonly=False,
    )
