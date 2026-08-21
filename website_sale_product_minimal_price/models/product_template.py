# Copyright 2019 Tecnativa - Sergio Teruel
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models
from odoo.fields import Domain
from odoo.http import request


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_website_current_pricelist(self, website=None):
        website = website or self.env["website"].get_current_website()
        if request and getattr(request, "pricelist", False):
            return request.pricelist
        pricelist = website._get_and_cache_current_pricelist()
        if pricelist:
            return pricelist
        return self.env.user.partner_id.property_product_pricelist

    def _get_product_subpricelists(self, pricelist):
        base_domain = pricelist._get_applicable_rules_domain(
            products=self, date=fields.Datetime.now()
        )
        domain = Domain.AND(
            [
                base_domain,
                [
                    ("compute_price", "=", "formula"),
                    ("base", "=", "pricelist"),
                    ("base_pricelist_id", "!=", False),
                ],
            ]
        )
        items = self.env["product.pricelist.item"].search(domain)
        return items.mapped("base_pricelist_id")

    def _get_variants_from_pricelist(self, pricelist):
        return pricelist.mapped("item_ids").filtered(
            lambda i: i.product_id in self.product_variant_ids
        )

    def _get_pricelist_variant_items(self, pricelist):
        res = self._get_variants_from_pricelist(pricelist)
        next_pricelists = self._get_product_subpricelists(pricelist)
        res |= self._get_variants_from_pricelist(next_pricelists)
        visited_pricelists = pricelist
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
        min_price = 99999999
        product_find = self.env["product.product"]
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
                product_price = product.with_context(
                    quantity=qty, pricelist=pricelist.id
                )._get_contextual_price()
                if product_price != min_price and min_price != 99999999:
                    # Mark if there are different prices iterating over
                    # variants and comparing qty 1 and maximum qty
                    has_distinct_price = True
                if product_price < min_price:
                    min_price = product_price
                    add_qty = qty
                    product_find = product
        return product_find, add_qty, has_distinct_price

    def _get_first_possible_combination(
        self, parent_combination=None, necessary_values=None
    ):
        """Get the cheaper product combination for the website view."""
        res = super()._get_first_possible_combination(
            parent_combination=parent_combination, necessary_values=necessary_values
        )
        context = self.env.context
        if context.get("website_id") and self.product_variant_count > 1:
            # It only makes sense to change the default one when there are
            # more than one variants and we know the pricelist
            current_website = self.env["website"].get_current_website()
            pricelist = self._get_website_current_pricelist(current_website)
            product = self._get_cheapest_info(pricelist)[0]
            # Rebuild the combination in the expected order
            res = self.env["product.template.attribute.value"]
            for line in product.valid_product_template_attribute_line_ids:
                value = product.product_template_attribute_value_ids.filtered(
                    lambda x, line=line: x in line.product_template_value_ids
                )
                if not value:
                    value = line.product_template_value_ids[:1]
                res += value
        return res

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1,
        uom_id=False,
        only_template=False,
    ):
        combination_info = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            uom_id=uom_id,
            only_template=only_template,
        )
        if only_template and not product_id:
            return combination_info
        combination = combination or self.env["product.template.attribute.value"]
        if only_template:
            product = self.env["product.product"]
        elif product_id:
            product = self.env["product.product"].browse(product_id)
            if combination - product.product_template_attribute_value_ids:
                # If the combination is not fully represented in the given product
                #   make sure to fetch the right product for the given combination
                product = self._get_variant_for_combination(combination)
        else:
            product = self._get_variant_for_combination(combination)
        if not product:
            # If no product is found, return the combination info without prices
            # the combination is not valid for the product or the product is archived
            return combination_info
        category_ids = []
        if product.categ_id and product.categ_id.parent_path:
            category_ids = list(map(int, product.categ_id.parent_path.split("/")[0:-1]))
        # Getting all min_quantity of the current product to compute the possible
        # price scale.
        qty_list = self.env["product.pricelist.item"].search(
            [
                "|",
                ("product_id", "=", product.id),
                "|",
                ("product_tmpl_id", "=", product.product_tmpl_id.id),
                ("categ_id", "in", category_ids),
                ("min_quantity", ">", 0),
            ]
        )
        qty_list = sorted(set(qty_list.mapped("min_quantity")))
        price_scale = []
        last_price = product.with_context(quantity=0)._get_contextual_price()
        for min_qty in qty_list:
            new_price = product.with_context(quantity=min_qty)._get_contextual_price()
            if new_price != last_price:
                price_scale.append(
                    {
                        "min_qty": min_qty,
                        "price": new_price,
                        "currency_id": combination_info["currency"].id,
                    }
                )
                last_price = new_price
        combination_info.update(
            uom_name=product.uom_id.name,
            minimal_price_scale=price_scale,
        )
        return combination_info

    def _get_minimal_search_price(self, website, mapping):
        self.ensure_one()
        pricelist = self._get_website_current_pricelist(website)
        product, add_qty, _has_distinct_price = self._get_cheapest_info(pricelist)
        product_price = product.with_context(
            quantity=add_qty, pricelist=pricelist.id
        )._get_contextual_price()
        return self.env["ir.qweb.field.monetary"].value_to_html(
            product_price,
            {"display_currency": mapping["detail"]["display_currency"]},
        )

    def _search_render_results(self, fetch_fields, mapping, icon, limit):
        results_data = super()._search_render_results(
            fetch_fields, mapping, icon, limit
        )
        if "detail" not in mapping:
            return results_data

        current_website = self.env["website"].get_current_website()
        for product, data in zip(self, results_data, strict=False):
            minimal_price = product._get_minimal_search_price(current_website, mapping)
            if minimal_price:
                data["price"] = minimal_price
                data.pop("list_price", None)
        return results_data

    def _get_sales_prices(self, website):
        prices = super()._get_sales_prices(website)
        pricelist = self._get_website_current_pricelist(website)
        for template in self.filtered("is_published"):
            price_info = prices[template.id]
            product, add_qty, has_distinct_price = template._get_cheapest_info(
                pricelist
            )
            product_price_info = template._get_additionnal_combination_info(
                product,
                quantity=add_qty,
                uom=product.uom_id,
                date=fields.Date.context_today(self),
                website=website,
            )
            price_info.update(
                distinct_prices=has_distinct_price,
                price=product_price_info["list_price"],
            )
        return prices
