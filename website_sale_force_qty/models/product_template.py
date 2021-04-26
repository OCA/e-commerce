# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    website_sale_force_qty = fields.Float(
        string="Force quantity in website", default=0.0,
        help="Limit the product to a specific quantity to be bought in the website."
        " Set to 0 to disable"
    )

    _sql_constraints = [
        ('website_sale_force_qty_positive',
         'CHECK(website_sale_force_qty >= 0)',
         'The forced quantity on the website can not be negative'),
    ]
