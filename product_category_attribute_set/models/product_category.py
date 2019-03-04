# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class ProductCategory(models.Model):
    """
    extend PT to allow extra attributes per category
    """
    _inherit = 'product.category'

    product_field_ids = fields.Many2many(
        comodel_name='ir.model.fields', string='Extra Attributes for category',
        help='These attributes are for the category',
        domain=lambda self: [
            ('model', '=', 'product.product')
        ]
    )
