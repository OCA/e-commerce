# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    product_sort_criteria = fields.Selection(
        related='website_id.default_product_sort_criteria',
        default_model='website',
        readonly=False,
    )
