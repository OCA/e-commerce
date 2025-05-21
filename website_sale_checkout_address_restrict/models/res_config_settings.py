# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    disable_express_checkout = fields.Boolean(
        string="Disable Express Checkout When Multiple Addresses",
        config_parameter="website_sale.disable_express_checkout",
        help="When enabled, removing the 'express' flag in cart and checkout "
        "requests so users always select an address.",
    )

    filter_child_shipping = fields.Boolean(
        string="Filter Shipping Addresses for Child Contacts",
        config_parameter="website_sale.filter_child_shipping",
        help="When enabled, child contacts will only see their own "
        "and their children’s delivery addresses at checkout.",
    )
