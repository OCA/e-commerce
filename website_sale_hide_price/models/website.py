# Copyright 2017 Tecnativa - David Vidal
# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.http import request


class Website(models.Model):
    _inherit = "website"

    website_show_price = fields.Boolean(compute="_compute_website_show_price")
    website_hide_price_default_message = fields.Char(
        string="Default Hidden price message",
        help="When the price is hidden on the website we can give the customer"
        "some tips on how to find it out.",
        translate=True,
    )
    show_hide_price_message_to_public = fields.Boolean(
        string="Show hidden price message to public users",
        help="When enabled, the hidden price message set on each product (or the"
        " default one) is also shown to public (not logged-in) users. By default"
        " it is only shown to logged-in users.",
    )

    def _compute_website_show_price(self):
        for rec in self:
            rec.website_show_price = request.env.user.partner_id.website_show_price
