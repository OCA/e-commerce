# Copyright 2026 Studio73
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    brand_filter_display_mode = fields.Selection(
        related="website_id.brand_filter_display_mode",
        readonly=False,
    )
