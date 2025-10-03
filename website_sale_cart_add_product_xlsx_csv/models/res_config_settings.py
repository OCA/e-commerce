# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    cart_import_button = fields.Boolean(
        string="Is the cart import button enabled?",
        related="website_id.cart_import_button",
        readonly=False,
    )

    cart_import_button_file_limit = fields.Float(
        string="Cart import button file size limit (MB)",
        related="website_id.cart_import_button_file_limit",
        readonly=False,
    )
