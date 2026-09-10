# Copyright 2026 Domatix (https://www.domatix.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class WebsiteSaleAssuranceConfig(models.TransientModel):
    _name = "website.sale.assurance.config"
    _description = "Assurance Icons Configuration"

    website_id = fields.Many2one(
        comodel_name="website",
        required=True,
        default=lambda self: self.env["website"].get_current_website(),
    )
    assurance_columns = fields.Selection(
        related="website_id.assurance_columns",
        readonly=False,
    )
