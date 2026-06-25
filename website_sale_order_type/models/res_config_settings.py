# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_type_id = fields.Many2one(
        related="website_id.sale_type_id",
        readonly=False,
        check_company=True,
        help="If set, this sale order type is used for all orders created "
        "from this website and takes precedence over the partner sale order type.",
    )
