# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    tax_toggle_preactivated = fields.Boolean(
        default=False,
        help="If enabled, the tax toggle will be active by default when entering the website.",
    )
