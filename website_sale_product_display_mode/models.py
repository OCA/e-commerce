# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class ProductTemplateDisplayMode(models.Model):
    _inherit = "product.template"

    display_mode = fields.Selection(
        [
            ('normal', 'Normal'),
            ('summary', 'Summary'),
            ('open', 'Open'),
            ('filled', 'Filled')
        ],
        string='Display Mode',
        default='normal',
        help="Set the display mode of the product"
    )
