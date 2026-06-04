# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    cart_empty_button = fields.Boolean(
        string="Is the cart empty button enabled?",
        related="website_id.cart_empty_button",
        readonly=False,
    )
