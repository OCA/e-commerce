# Copyright 2020 Tecnativa - Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    published_in_product_category_snippet = fields.Boolean(
        "Published in product category snippet", copy=False
    )
    snippet_website_ids = fields.Many2many(
        "website",
        "product_public_category_snippet_website_rel",
        "product_public_category_id",
        "website_id",
        string="Websites for category snippet",
        help="Show this category in the product category snippet only on the "
        "selected websites. Leave empty to show it on all websites.",
        copy=False,
    )
