# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    regular_products_menu_label = fields.Char(
        default="My Regular Products",
        translate=True,
        help="Label of the 'My Regular Products' link in the shop categories "
        "and of the card on the customer portal.",
    )
    regular_products_card_text = fields.Char(
        default="Products you bought before, to buy again",
        translate=True,
        help="Description of the 'My Regular Products' card on the customer portal.",
    )
