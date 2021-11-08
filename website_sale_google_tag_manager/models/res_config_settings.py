# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    google_tag_manager_enhanced_conversions = fields.Boolean(
        related="website_id.google_tag_manager_enhanced_conversions", readonly=False
    )
