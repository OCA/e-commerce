# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    has_variant_price_extra = fields.Boolean(
        compute='_compute_has_variant_price_extra',
        store=True,
        string='Has variants with price extra',
    )

    @api.depends(
        'product_variant_ids.attribute_value_ids.price_ids.price_extra')
    def _compute_has_variant_price_extra(self):
        for template in self:
            if (template.product_variant_count and len(set(
                    template.product_variant_ids.mapped('price_extra'))) != 1):
                template.has_variant_price_extra = True

    def _website_price(self):
        templates = self.filtered(
            lambda x: (
                x.product_variant_count > 1 and any(
                    [v.price_extra != 0.0 for v in x.product_variant_ids]))
        )
        super(ProductTemplate, self - templates)._website_price()
        for product in templates:
            variant = product.product_variant_ids.sorted(
                key=lambda v: v.price_extra)[:1]
            product.website_price = variant.website_price
            product.website_public_price = variant.website_public_price
            product.website_price_difference = variant.website_price_difference
