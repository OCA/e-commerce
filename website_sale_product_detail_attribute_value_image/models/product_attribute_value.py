# Copyright 2020 Tecnativa - Alexandre D. Díaz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    website_product_detail_image = fields.Binary(
        string='Website detail image',
        attachment=True,
        help='Image of the attribute value for shop online product detail.',
    )
    website_product_detail_image_published = fields.Boolean(
        string='Publish detail image in website',
        help='Display attribute value image in shop online product detail',
    )
    website_name = fields.Char(string='Website name', translate=True)
