# Copyright 2020 Jairo Llopis - Tecnativa
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
        website = self.env["website"].get_current_website(fallback=False)
        if not website:
            return combination_info
        partner = self.env.user.partner_id
        company_id = website.company_id
        pricelist = website._get_current_pricelist()
        product = (
            self.env["product.product"].browse(combination_info["product_id"]) or self
        )
        # The list_price is always the price of one.
        quantity_1 = 1
        # Obtain the inverse field of the normal b2b/b2c behavior
        alt_field = (
            "total_excluded"
            if website.show_line_subtotals_tax_selection == "tax_included"
            else "total_included"
        )
        # Obtain taxes that apply to the product and context
        taxes = partner.property_account_position_id.map_tax(
            product.sudo().taxes_id.filtered(lambda x: x.company_id == company_id)
        ).with_context(force_price_include=alt_field == "total_excluded")
        # Obtain alt prices
        # TODO Cache upstream calls to compute_all() and get results from there
        alt_list_price = alt_price = taxes.compute_all(
            combination_info["price"],
            pricelist.currency_id,
            quantity_1,
            product,
            partner,
        )[alt_field]
        if combination_info.get("has_discounted_price"):
            alt_list_price = taxes.compute_all(
                combination_info["list_price"],
                pricelist.currency_id,
                quantity_1,
                product,
                partner,
            )[alt_field]
        combination_info.update(
            alt_price=alt_price, alt_list_price=alt_list_price, alt_field=alt_field
        )
        return combination_info

    def _get_sales_prices(self, pricelist, fiscal_position):
        prices = super()._get_sales_prices(pricelist, fiscal_position)
        for template in self:
            website = self.env["website"].get_current_website(fallback=False)
            company_id = website.company_id
            pricelist = website.pricelist_id
            partner = self.env.user.partner_id
            combination_info = template._get_combination_info()
            quantity_1 = 1
            alt_field = (
                "total_excluded"
                if website.show_line_subtotals_tax_selection == "tax_included"
                else "total_included"
            )
            taxes = partner.property_account_position_id.map_tax(
                template.sudo().taxes_id.filtered(
                    lambda x, company_id=company_id: x.company_id == company_id
                )
            ).with_context(force_price_include=alt_field == "total_excluded")

            alt_list_price = alt_price = taxes.compute_all(
                combination_info["price"],
                pricelist.currency_id,
                quantity_1,
                template,
                partner,
            )[alt_field]
            if combination_info.get("has_discounted_price"):
                alt_list_price = taxes.compute_all(
                    combination_info["list_price"],
                    pricelist.currency_id,
                    quantity_1,
                    template,
                    partner,
                )[alt_field]
            combination_info.update(
                alt_price=alt_price, alt_list_price=alt_list_price, alt_field=alt_field
            )
            combination_info = {"combination_info": combination_info}
            prices[template.id].update(combination_info)
        return prices
