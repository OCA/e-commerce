# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    regular_products_limit = fields.Integer(
        default=10, config_parameter="website_sale_menu_partner_top_selling.limit"
    )
