# Copyright 2026 Domatix (https://www.domatix.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class WebsiteSaleAssurance(models.Model):
    _name = "website.sale.assurance"
    _description = "Website Sale Assurance"
    _order = "sequence, id"

    name = fields.Char(
        required=True,
        help="Short benefit text, for instance '30-day money-back guarantee'.",
    )
    subtitle = fields.Char(
        help="Optional second line, for instance 'On the mechanism'.",
    )
    icon = fields.Char(
        help="Icon name. A Font Awesome class (e.g. 'fa-truck') or a Lucide "
        "icon name (e.g. 'shield-check') if Lucide is loaded on the website.",
    )
    image = fields.Binary(
        help="Optional icon image. When set, it is used instead of the icon name.",
    )
    url = fields.Char(help="Click through URL, for instance '/shipping'.")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    website_id = fields.Many2one(
        comodel_name="website",
        ondelete="cascade",
        help="When empty, the item is shown on every website.",
    )
