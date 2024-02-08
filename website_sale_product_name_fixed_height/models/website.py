# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Website(models.Model):
    _inherit = "website"

    @api.constrains("row_count")
    def _check_row_count(self):
        for record in self:
            if record.row_count < 1:
                raise ValidationError(_("Row count must be greater than 0"))

    row_count = fields.Integer(
        string="Row count in description",
        default=1,
        help="Number of rows to display in description",
    )
