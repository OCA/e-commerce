# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    has_distinct_variant_price = fields.Boolean(
        compute='_compute_has_distinct_variant_price',
        string='Has variants with distinct price extra',
    )

    def _compute_has_distinct_variant_price(self):
        for template in self:
            if template.product_variant_count > 1:
                prices = template.product_variant_ids.mapped('website_price')
                if len(prices) > 1:
                    template.has_distinct_variant_price = True

    def _get_combination_info(
        self, combination=False, product_id=False, add_qty=1, pricelist=False,
            parent_combination=False, only_template=False):
        """
        Update product template prices for products items view in website shop
        render with cheaper variant prices.
        """
        combination_info = super()._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty,
            pricelist=pricelist, parent_combination=parent_combination,
            only_template=only_template)

        if (only_template and self.env.context.get('website_id') and
                self.product_variant_count > 1):
            cheaper_variant = self.product_variant_ids.sorted(
                key=lambda p: p.website_price)[:1]

            res = cheaper_variant._get_combination_info_variant()

            combination_info.update({
                'price': res.get('price'),
                'list_price': res.get('list_price'),
                'has_discounted_price': res.get('has_discounted_price'),
            })
        return combination_info

    def _get_first_possible_combination(
            self, parent_combination=None, necessary_values=None):
        """
        Get the cheaper product combination for the product for website view.
        We only take into account attributes that generate variants and
        products with more than one variant.
        """
        combination = super()._get_first_possible_combination(
            parent_combination=parent_combination,
            necessary_values=necessary_values
        )
        if (self.env.context.get('website_id') and
                self.product_variant_count > 1):
            ptav_obj = self.env['product.template.attribute.value']
            pav = self.product_variant_ids.sorted(
                'website_price')[:1].attribute_value_ids
            cheaper_combination = ptav_obj.search([
                ('product_tmpl_id', '=', self.id),
                ('product_attribute_value_id', 'in', pav.ids),
            ])
            variant_combination = combination.filtered(
                lambda x: x.attribute_id.create_variant == 'always')
            combination_returned = cheaper_combination + (
                combination - variant_combination)
            # Keep order to avoid This combination does not exist message
            return combination_returned.sorted(
                lambda x: x.attribute_id.sequence)
        return combination
