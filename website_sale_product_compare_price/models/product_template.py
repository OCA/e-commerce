# Copyright 2026 Domatix
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models
from odoo.http import request
from odoo.tools import formatLang

# Minimum discount (as a percentage of the reference price) to display the
# compare price block. Lower values are treated as rounding noise.
MIN_DISCOUNT_PERCENT = 1.0


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_variant_compare_price(self, product, website):
        """Sales price of the variant (list price + price extra) ready to be
        shown as the crossed-out reference price.

        The effective price computed by ``website_sale`` keeps this variant
        sales price as its reference, so the reference is converted to the
        website currency and loaded with the same taxes as
        ``combination_info['price']``.
        """
        self.ensure_one()
        product.ensure_one()
        compare_price = product.lst_price or 0.0
        if not compare_price:
            return 0.0
        src_currency = product.currency_id
        if src_currency and src_currency != website.currency_id:
            compare_price = src_currency._convert(
                compare_price,
                website.currency_id,
                website.company_id,
                fields.Date.context_today(self),
                round=False,
            )
        product_taxes = product.sudo().taxes_id._filter_taxes_by_company(
            website.company_id
        )
        if product_taxes:
            fiscal_position = getattr(
                request, "fiscal_position", self.env["account.fiscal.position"]
            )
            taxes = fiscal_position.map_tax(product_taxes)
            compare_price = self._apply_taxes_to_price(
                compare_price,
                website.currency_id,
                product_taxes,
                taxes,
                product,
                website=website,
            )
        return compare_price

    def _get_compare_discount_percent(self, real_price, compare_price):
        """Discount of the effective price over the reference price as an
        integer percentage, or 0 when there is no significant discount.
        """
        if not compare_price or compare_price <= real_price:
            return 0
        percent = (compare_price - real_price) * 100.0 / compare_price
        if percent < MIN_DISCOUNT_PERCENT:
            return 0
        return int(round(percent))

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1.0,
        uom_id=False,
        only_template=False,
    ):
        """Enrich the combination info with the compare price info.

        Two references are supported, following the native ``website_sale``
        behaviour:

        * the variant sales price, when a pricelist rule that is not shown
          natively (e.g. a fixed price) lowers the effective price;
        * the manual *Compare to Price* field of the template.

        The native discount strikethrough (``has_discounted_price``) keeps its
        own behaviour. The compare info is only computed on the frontend and
        when the *Comparison Price* feature is enabled.
        """
        combination_info = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            uom_id=uom_id,
            only_template=only_template,
        )
        combination_info.update(
            {
                "has_compare_price": False,
                "compare_badge_text": False,
                "compare_save_text": False,
            }
        )
        if not self.env.context.get("website_id"):
            return combination_info
        real_price = combination_info.get("price") or 0.0
        if not real_price or combination_info.get("has_discounted_price"):
            return combination_info
        if not self.env["res.groups"]._is_feature_enabled(
            "website_sale.group_product_price_comparison"
        ):
            return combination_info

        website = self.env["website"].get_current_website()
        compare_price = 0.0
        has_compare_price = False
        if not only_template:
            product = (
                self.env["product.product"]
                .sudo()
                .browse(combination_info.get("product_id"))
            )
            if product:
                compare_price = self._get_variant_compare_price(product, website)
                has_compare_price = compare_price > real_price
        if not has_compare_price:
            compare_price = combination_info.get("compare_list_price") or 0.0
        percent = self._get_compare_discount_percent(real_price, compare_price)
        if not percent:
            return combination_info
        currency = website.currency_id
        combination_info.update(
            {
                "compare_price": compare_price,
                "compare_price_formatted": formatLang(
                    self.env, compare_price, currency_obj=currency
                ),
                "has_compare_price": has_compare_price,
                "compare_badge_text": f"-{percent}%",
                "compare_save_text": self.env._(
                    "You save %s",
                    formatLang(
                        self.env, compare_price - real_price, currency_obj=currency
                    ),
                ),
            }
        )
        return combination_info
