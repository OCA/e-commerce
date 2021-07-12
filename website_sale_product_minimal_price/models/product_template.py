# Copyright 2019 Tecnativa - Sergio Teruel
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_product_subpricelists(self, pricelist_id):
        return pricelist_id.item_ids.filtered(
            lambda i: (
                i.applied_on == "3_global"
                or (
                    i.applied_on == "2_product_category" and i.categ_id == self.categ_id
                )
                or (i.applied_on == "1_product" and i.product_tmpl_id == self)
                or (
                    i.applied_on == "0_product_variant"
                    and i.product_id in self.product_variant_ids
                )
            )
            and i.compute_price == "formula"
            and i.base == "pricelist"
        ).mapped("base_pricelist_id")

    def _get_variants_from_pricelist(self, pricelist_ids):
        return pricelist_ids.mapped("item_ids").filtered(
            lambda i: i.product_id in self.product_variant_ids
        )

    def _get_pricelist_variant_items(self, pricelist_id):
        res = self._get_variants_from_pricelist(pricelist_id)
        next_pricelists = self._get_product_subpricelists(pricelist_id)
        res |= self._get_variants_from_pricelist(next_pricelists)
        visited_pricelists = pricelist_id
        while next_pricelists:
            pricelist = next_pricelists[0]
            if pricelist not in visited_pricelists:
                res |= self._get_variants_from_pricelist(pricelist)
                next_pricelists |= self._get_product_subpricelists(pricelist)
                next_pricelists -= pricelist
                visited_pricelists |= pricelist
            else:
                next_pricelists -= pricelist
        return res

    def _get_cheapest_info(self, pricelist):
        """Helper method for getting the variant with lowest price."""
        # TODO: Cache this method for getting better performance
        self.ensure_one()
        context = dict(self.env.context, pricelist=pricelist.id)
        min_price = 99999999
        product_id = False
        add_qty = 0
        has_distinct_price = False
        # Variants with extra price
        variants_extra_price = self.product_variant_ids.filtered("price_extra")
        variants_without_extra_price = self.product_variant_ids - variants_extra_price
        # Avoid compute prices when pricelist has not item variants defined
        variant_items = self._get_pricelist_variant_items(pricelist)
        if variant_items:
            # Take into account only the variants defined in pricelist and one
            # variant not defined to compute prices defined at template or
            # category level. Maybe there is any definition on template that
            # has cheaper price.
            variants = variant_items.mapped("product_id")
            products = variants + (self.product_variant_ids - variants)[:1]
        else:
            products = variants_without_extra_price[:1]
        products |= variants_extra_price
        for product in products:
            for qty in [1, 99999999]:
                context = dict(context, quantity=qty)
                product_price = product.with_context(context).price
                if product_price != min_price and min_price != 99999999:
                    # Mark if there are different prices iterating over
                    # variants and comparing qty 1 and maximum qty
                    has_distinct_price = True
                if product_price < min_price:
                    min_price = product_price
                    add_qty = qty
                    product_id = product.id
        return product_id, add_qty, has_distinct_price

    def _get_first_possible_combination(
        self, parent_combination=None, necessary_values=None
    ):
        """Get the cheaper product combination for the website view."""
        res = super()._get_first_possible_combination(
            parent_combination=parent_combination, necessary_values=necessary_values
        )
        context = self.env.context
        if (
            context.get("website_id")
            and context.get("pricelist")
            and self.product_variant_count > 1
        ):
            # It only makes sense to change the default one when there are
            # more than one variants and we know the pricelist
            pricelist = self.env["product.pricelist"].browse(context["pricelist"])
            product_id = self._get_cheapest_info(pricelist)[0]
            product = self.env["product.product"].browse(product_id)
            # Rebuild the combination in the expected order
            res = self.env["product.template.attribute.value"]
            for line in product.valid_product_template_attribute_line_ids:
                value = product.product_template_attribute_value_ids.filtered(
                    lambda x: x in line.product_template_value_ids
                )
                if not value:
                    value = line.product_template_value_ids[:1]
                res += value
        return res
