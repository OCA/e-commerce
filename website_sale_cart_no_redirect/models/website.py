# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    cart_add_on_page = fields.Boolean("Stay on page after adding to cart")
