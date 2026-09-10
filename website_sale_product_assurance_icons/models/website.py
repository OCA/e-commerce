# Copyright 2026 Domatix (https://www.domatix.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class Website(models.Model):
    _inherit = "website"

    assurance_columns = fields.Selection(
        selection=[
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
        ],
        default="4",
        string="Assurance Icons Columns",
        help="Number of columns used to display the assurance icons block.",
    )

    @api.model
    def _get_assurance_records(self):
        self.ensure_one()
        return (
            self.env["website.sale.assurance"]
            .search(
                [
                    ("active", "=", True),
                    "|",
                    ("website_id", "=", False),
                    ("website_id", "=", self.id),
                ]
            )
            .sorted("sequence")
        )
