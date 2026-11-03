# Copyright 2022 Tecnativa - David Vidal
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
        add_qty=1.0,
        uom_id=False,
        only_template=False,
        pricelist=None,
        fiscal_position=None,
    ):
        website = self.env.website
        if pricelist is None and not request:
            pricelists = (
                website.get_pricelist_available()
                if website
                else self.env["product.pricelist"]
            )
            pricelist = pricelists[:1] or self.env["product.pricelist"]
        if fiscal_position is None and not request:
            fiscal_position = self.env["account.fiscal.position"]

        combination_info = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            uom_id=uom_id,
            only_template=only_template,
            pricelist=pricelist,
            fiscal_position=fiscal_position,
        )
        website = self.env.website
        website_show_price = website.website_show_price if website else True
        hide_price = bool(self.website_hide_price or not website_show_price)
        combination_info.update(
            {
                "website_hide_price": self.website_hide_price,
                "website_hide_price_message": self.website_hide_price_message,
                "hide_price": hide_price or combination_info.get("hide_price", False),
                "prevent_sale": hide_price
                or combination_info.get("prevent_sale", False),
            }
        )
        if hide_price:
            combination_info.update(
                {
                    "price": 0.0,
                    "list_price": 0.0,
                    "raw_pricelist_price": 0.0,
                    "compare_list_price": 0.0,
                    "base_unit_price": 0.0,
                }
            )
        return combination_info

    def _search_render_results(self, fetch_fields, mapping, icon, limit):
        """Hide price on the search bar results"""
        results_data = super()._search_render_results(
            fetch_fields, mapping, icon, limit
        )
        website = self.env.website
        website_show_price = website.website_show_price if website else True
        for product, data in zip(self, results_data, strict=True):
            if product.website_hide_price or not website_show_price:
                msg = (
                    product.website_hide_price_message
                    or (website and website.website_hide_price_default_message)
                    or ""
                )
                data.update(
                    {
                        "price": (f"<span>{msg}</span>") if msg else "",
                        "list_price": "",
                    }
                )
        return results_data

    def _website_show_quick_add(self, product=None):
        website = self.env.website
        website_show_price = website.website_show_price if website else True
        if self.website_hide_price or not website_show_price:
            return False
        return super()._website_show_quick_add(product=product)
