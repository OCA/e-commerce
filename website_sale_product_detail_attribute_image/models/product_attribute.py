# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    website_product_detail_image = fields.Binary(
        string="Website detail image",
        attachment=True,
        help="Image of the attribute for shop online product detail.",
    )
    website_product_detail_image_published = fields.Boolean(
        string="Publish in website",
        help="Display attribute image in shop online product detail",
    )
    website_name = fields.Char(string="Website name", translate=True)


class ProductAttributevalue(models.Model):
    _inherit = "product.attribute.value"

    website_name = fields.Char(string="Website value", translate=True)
