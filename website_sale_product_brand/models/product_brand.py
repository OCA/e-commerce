# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class ProductBrand(models.Model):
    _name = "product.brand"
    _inherit = ["product.brand", "website.published.mixin"]

    published_products_count = fields.Integer(
        compute="_compute_published_products_count",
    )

    def _default_is_published(self):
        return True

    def _compute_published_products_count(self):
        for brand in self:
            brand.published_products_count = self.env["product.template"].search_count(
                [
                    ("product_brand_id", "=", brand.id),
                    ("website_published", "=", True),
                ]
            )
