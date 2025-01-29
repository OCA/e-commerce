# Copyright 2020 Jairo Llopis - Tecnativa
# Copyright 2024 Carlos Lopez - Tecnativa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1,
        parent_combination=False,
        only_template=False,
    ):
        """Include alternative (un)taxed amount."""
        combination_info = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            parent_combination=parent_combination,
            only_template=only_template,
        )
        product = (
            self.env["product.product"].browse(combination_info["product_id"]) or self
        )
        combination_info.update(
            self._get_alt_prices(
                product,
                combination_info["list_price"],
                combination_info["price"],
                combination_info["has_discounted_price"],
            )
        )
        return combination_info

    def _get_sales_prices(self, website):
        res = super()._get_sales_prices(website)
        currency = website.currency_id
        for template in self:
            price_info = res[template.id]
            list_price = price_info.get("base_price") or price_info["price_reduce"]
            price = price_info["price_reduce"]
            has_discounted_price = currency.compare_amounts(list_price, price) == 1
            alt_price_info = self._get_alt_prices(
                template, list_price, price, has_discounted_price
            )
            price_info.update(alt_price_info, has_discounted_price=has_discounted_price)
        return res

    def _get_alt_prices(self, product, list_price, price, has_discounted_price):
        website = self.env["website"].get_current_website(fallback=False)
        if not website:
            return {}
        partner = self.env.user.partner_id
        company_id = website.company_id
        pricelist = website.pricelist_id
        # The list_price is always the price of one.
        quantity_1 = 1
        # Obtain the inverse field of the normal b2b/b2c behavior
        alt_field = (
            "total_included"
            if website.show_line_subtotals_tax_selection == "tax_excluded"
            else "total_excluded"
        )
        # Obtain taxes that apply to the product and context
        taxes = partner.property_account_position_id.map_tax(
            product.sudo().taxes_id.filtered(lambda x: x.company_id == company_id)
        ).with_context(force_price_include=alt_field == "total_excluded")
        # Obtain alt prices
        # TODO Cache upstream calls to compute_all() and get results from there
        alt_list_price = alt_price = taxes.compute_all(
            price,
            pricelist.currency_id,
            quantity_1,
            product,
            partner,
        )[alt_field]
        if has_discounted_price:
            alt_list_price = taxes.compute_all(
                list_price,
                pricelist.currency_id,
                quantity_1,
                product,
                partner,
            )[alt_field]
        return {
            "alt_price": alt_price,
            "alt_list_price": alt_list_price,
            "alt_field": alt_field,
        }
