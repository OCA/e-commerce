# Copyright 2019 Tecnativa - Sergio Teruel
# Copyright 2020 Tecnativa - Carlos Roca
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
import math


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_cheapest_info(self, pricelist):
        """Helper method for getting the variant with lowest price."""
        # TODO: Cache this method for getting better performance
        self.ensure_one()
        context = dict(self.env.context, pricelist=pricelist.id)
        min_price = math.inf
        product_id = False
        add_qty = 0
        has_distinct_price = False
        for product in self.product_variant_ids:
            for qty in [1, math.inf]:
                context = dict(context, quantity=qty)
                product_price = product.with_context(context).price
                if product_price != min_price and min_price != math.inf:
                    # Mark if there are different prices iterating over
                    # variants and comparing qty 1 and maximum qty
                    has_distinct_price = True
                if product_price < min_price:
                    min_price = product_price
                    add_qty = qty
                    product_id = product.id
        return product_id, add_qty, has_distinct_price

    def _get_combination_info(
        self, combination=False, product_id=False, add_qty=1, pricelist=False,
            parent_combination=False, only_template=False):
        """Update product template prices for products items view in website
        shop render with cheaper variant prices. We are testing both edges for
        quantity, considering that one of them will be the cheaper one.
        """
        self.ensure_one()
        has_distinct_price = False
        if pricelist and "bin_size" in self.env.context:
            # This key in the context indicates that we are on the grid view,
            # for avoiding problems on the product view
            # FIXME: Find an stronger condition for this - Check only_template?
            only_template = False
            product_id, add_qty, has_distinct_price = self._get_cheapest_info(
                pricelist)
        res = super()._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty,
            pricelist=pricelist, parent_combination=parent_combination,
            only_template=only_template)
        # Inject the boolean for telling if putting "From " text before price
        res["has_distinct_price"] = has_distinct_price
        return res

    def _get_first_possible_combination(
            self, parent_combination=None, necessary_values=None):
        """Get the cheaper product combination for the website view."""
        res = super()._get_first_possible_combination(
            parent_combination=parent_combination,
            necessary_values=necessary_values
        )
        context = self.env.context
        if (context.get("website_id") and context.get("pricelist") and
                self.product_variant_count > 1):
            # It only makes sense to change the default one when there are
            # more than one variants and we know the pricelist
            pricelist = self.env["product.pricelist"].browse(
                context["pricelist"])
            product_id = self._get_cheapest_info(pricelist)[0]
            product = self.env["product.product"].browse(product_id)
            ptavs = product.product_template_attribute_value_ids
            variant_attributes = ptavs.mapped("attribute_id")
            # remove returned values that are variant specific
            res.filtered(lambda x: x.attribute_id not in variant_attributes)
            # and inject cheapest variant ones
            res += ptavs
        return res
