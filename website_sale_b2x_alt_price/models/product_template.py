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
        pricelist=False,
        parent_combination=False,
        only_template=False,
    ):
        """Include alternative (un)taxed amount."""
        combination_info = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            parent_combination=parent_combination,
            only_template=only_template,
        )
        website = self.env["website"].get_current_website(fallback=False)
        if not website:
            return combination_info
        partner = self.env.user.partner_id
        company_id = website.company_id
        pricelist = pricelist or website.get_current_pricelist()
        product = (
            self.env["product.product"].browse(
                combination_info["product_id"])
            or self
        )
        # The list_price is always the price of one.
        quantity_1 = 1
        # Obtain the inverse field of the normal b2b/b2c behavior
        alt_field = (
            "total_included"
            if self.env.user.has_group(
                "account.group_show_line_subtotals_tax_excluded"
            )
            else "total_excluded"
        )
        # Obtain taxes that apply to the product and context
        taxes = partner.property_account_position_id.map_tax(
            product.sudo().taxes_id.filtered(
                lambda x: x.company_id == company_id),
            product,
            partner,
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
            alt_price=alt_price,
            alt_list_price=alt_list_price,
            alt_field=alt_field
        )
        return combination_info
