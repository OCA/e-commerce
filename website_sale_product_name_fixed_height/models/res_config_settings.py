# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    row_count = fields.Integer(
        related="website_id.row_count",
        help="Number of rows to display in description",
        readonly=False,
    )
