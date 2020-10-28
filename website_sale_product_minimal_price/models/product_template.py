# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, tools


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_combination_info(
        self, combination=False, product_id=False, add_qty=1, pricelist=False,
            parent_combination=False, only_template=False):
        """
        Update product template prices for products items view in website shop
        render with cheaper variant prices.
        Checking the context, we can know if we are on grid view or at the product view.
        With this comprobation we avoid problems rendering the price at the product
        view.
        """
        has_pricelist_items = False
        quantity = self.env.context.get('quantity', add_qty)
        context = dict(
            self.env.context,
            quantity=quantity,
            pricelist=pricelist.id if pricelist else False
        )
        product_template = self.with_context(context)
        combination = combination or product_template.env[
            'product.template.attribute.value']
        if product_id and not combination:
            product = product_template.env['product.product'].browse(product_id)
        else:
            product = product_template._get_variant_for_combination(combination)
        if pricelist and "bin_size" in self.env.context:
            # In this version the categories are not contempled.
            today = fields.Date.today()
            pricelist_items = pricelist.item_ids.filtered(
                lambda i: i.product_tmpl_id.id == self.id
                or i.product_id.product_tmpl_id.id == self.id
                and i.min_quantity > add_qty
                and (not i.date_start or i.date_start <= today)
                and (not i.date_end or today <= i.date_end))
            has_pricelist_items = bool(pricelist_items)
            if product:
                min_price = product.list_price
                for item in pricelist_items:
                    final_price = item.fixed_price
                    price = product.list_price
                    price_limit = product.list_price
                    if item.compute_price == 'formula':
                        price = (
                            price_limit - (price_limit * item.price_discount) / 100
                        )
                        if item.price_round:
                            price = tools.float_round(
                                price, precision_rounding=item.price_round)
                        if item.price_surcharge:
                            price += item.price_surcharge
                        if item.price_min_margin:
                            price = max(price, price_limit + item.price_min_margin)
                        if item.price_max_margin:
                            price = min(price, price_limit + item.price_max_margin)
                        final_price = price
                    elif item.compute_price == 'percentage':
                        final_price = (
                            product.list_price - (
                                product.list_price * item.percent_price) / 100
                        )
                    if final_price < min_price:
                        add_qty = item.min_quantity
                        min_price = final_price
        combination_info = super()._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty,
            pricelist=pricelist, parent_combination=parent_combination,
            only_template=only_template)
        if (only_template and self.env.context.get('website_id') and
                (self.product_variant_count > 1 or has_pricelist_items)):
            cheaper_variant = self.product_variant_ids.sorted(
                key=lambda p: p._get_combination_info_variant(
                    pricelist=pricelist
                )['price']
            )[:1]

            res = cheaper_variant._get_combination_info_variant(pricelist=pricelist)

            combination_info.update({
                'price': res.get('price'),
                'list_price': res.get('list_price'),
                'has_discounted_price': res.get('has_discounted_price'),
                'has_distinct_price': True,
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
