# Copyright 2022 Tecnativa - David Vidal
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    website_hide_price_default_message = fields.Char(
        related="website_id.website_hide_price_default_message", readonly=False,
    )
