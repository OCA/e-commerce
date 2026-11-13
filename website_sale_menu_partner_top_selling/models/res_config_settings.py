# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    regular_products_limit = fields.Integer(
        default=10, config_parameter="website_sale_menu_partner_top_selling.limit"
    )
    regular_products_period_days = fields.Integer(
        string="Regular Products Period (Days)",
        default=0,
        config_parameter="website_sale_menu_partner_top_selling.period_days",
        help="Only count orders from the last days. Set to 0 to count all orders.",
    )
    regular_products_menu_label = fields.Char(
        string="Regular Products Menu Label",
        related="website_id.company_id.regular_products_menu_label",
        readonly=False,
    )
    regular_products_portal_card = fields.Boolean(
        string="Customer Portal Card",
        default=False,
        config_parameter="website_sale_menu_partner_top_selling.portal_card",
        help="Show a 'My Regular Products' card on the customer portal home page.",
    )
