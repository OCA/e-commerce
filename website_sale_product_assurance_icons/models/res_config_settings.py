# Copyright 2026 Domatix (https://www.domatix.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    assurance_columns = fields.Selection(
        related="website_id.assurance_columns",
        readonly=False,
    )
