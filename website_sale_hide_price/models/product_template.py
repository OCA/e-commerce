# Copyright 2022 Tecnativa - David Vidal
# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models
from odoo.http import request


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
        combination_info.update(
            {
                "website_hide_price": self.website_hide_price,
                "website_hide_price_message": self.website_hide_price_message,
            }
        )
        return combination_info

    def _website_hide_price_combination_info(self, combination_info):
        """Remove the hidden prices from a combination info sent to the browser.

        Only for JSON responses: server-rendered templates already hide the
        prices, and zeroing them there would show "0.00" in the blocks that do
        not check the hidden price (e.g. suggested products).
        """
        self.ensure_one()
        if not self._website_price_hidden():
            return combination_info
        for key in ("price", "list_price", "compare_list_price", "base_unit_price"):
            if key in combination_info:
                combination_info[key] = 0.0
        combination_info["has_discounted_price"] = False
        # Tells consumers the 0.0 prices are hidden, not free
        combination_info["website_hide_price"] = True
        if combination_info.get("product_tracking_info"):
            combination_info["product_tracking_info"] = dict(
                combination_info["product_tracking_info"], price=0.0
            )
        return combination_info

    def _website_price_hidden(self):
        """Return whether the current website visitor must not see the price."""
        self.ensure_one()
        if not request:
            return False
        website = self.env["website"].get_current_website()
        return not website.website_show_price or self.website_hide_price

    def _website_hide_price_blocks_cart(self):
        """Return whether a hidden price prevents adding the product to the cart."""
        return self._website_price_hidden()

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
        # The /shop tile button, same check as the variant override
        return (
            not self._website_hide_price_blocks_cart()
            and super()._website_show_quick_add()
        )
