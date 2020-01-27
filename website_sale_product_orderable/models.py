# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class ProductTemplateOrderable(models.Model):
    _inherit = "product.template"

    orderable = fields.Boolean(
        default=True,
        help="Check if you want to set the product as orderable."
    )
    not_available_display_message = fields.Text(
        translate=True,
        help="Text that will be displayed if the product is set as not orderable"
    )
