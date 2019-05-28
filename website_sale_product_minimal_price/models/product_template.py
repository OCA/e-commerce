# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    has_distinct_variant_price = fields.Boolean(
        compute='_compute_has_distinct_variant_price',
        string='Has variants with distinct extra',
    )

    def _compute_has_distinct_variant_price(self):
        for template in self:
            if template.product_variant_count > 1:
                prices = template.product_variant_ids.mapped('website_price')
                if len(prices) > 1:
                    template.has_distinct_variant_price = True

    def _website_price(self):
        templates = self.filtered(lambda x: x.product_variant_count > 1)
        super(ProductTemplate, self - templates)._website_price()
        for product in templates:
            variant = product.product_variant_ids.sorted(
                key=lambda p: p.website_price)[:1]
            product.website_price = variant.website_price
            product.website_public_price = variant.website_public_price
            product.website_price_difference = variant.website_price_difference
