# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    website_hide_price = fields.Boolean(string="Hide prices on website")
    website_hide_price_message = fields.Text(
        string="Hidden price message",
        help="When the price is hidden on the website we can give the customer"
        "some tips on how to find it out.",
        translate=True,
    )

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1,
        parent_combination=False,
        only_template=False,
    ):
        combination_info = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            parent_combination=parent_combination,
            only_template=only_template,
        )
        combination_info.update(
            {
                "website_hide_price": self.website_hide_price,
                "website_hide_price_message": self.website_hide_price_message,
            }
        )
        return combination_info

    def _search_render_results(self, fetch_fields, mapping, icon, limit):
        """Hide price on the search bar results"""
        results_data = super()._search_render_results(
            fetch_fields, mapping, icon, limit
        )
        website_show_price = (
            self.env["website"].get_current_website().website_show_price
        )
        for product, data in zip(self, results_data, strict=True):
            if product.website_hide_price or not website_show_price:
                data.update(
                    {
                        "price": "<span>%s</span>"
                        % (product.website_hide_price_message or ""),
                        "list_price": "",
                    }
                )
        return results_data

    def _website_show_quick_add(self):
        website_show_price = (
            self.env["website"].get_current_website().website_show_price
        )
        return (
            website_show_price and not self.website_hide_price
        ) and super()._website_show_quick_add()
