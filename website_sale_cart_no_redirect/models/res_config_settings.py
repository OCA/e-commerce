# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    cart_add_on_page = fields.Boolean(
        "Stay on page after adding to cart",
        related="website_id.cart_add_on_page",
        readonly=False,
    )
