# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http, tools
from odoo.http import request
from odoo import fields


class WebsiteSaleProductDetailAttributeImage(WebsiteSale):

    @http.route(['/sale/get_combination_info_pricelist_atributes'],
                type='json',
                auth="public",
                website=True)
    def get_combination_info_pricelist_atributes(
            self, product_id, actual_qty, **kwargs):
        """Special route to use website logic in get_combination_info override.
        This route is called in JS by appending _website to the base route.
        """
        actual_qty = int(actual_qty)
        product = request.env["product.product"].browse(product_id)
        current_website = request.env["website"].get_current_website()
        today = fields.Date.today()
        res = []
        pricelist = current_website.get_current_pricelist()
        pricelist_variant_items = pricelist.item_ids.filtered(
            lambda i: i.product_id.id == product.id
            and (not i.date_start or i.date_start <= today)
            and (not i.date_end or today <= i.date_end)
            and i.min_quantity > 0)
        if pricelist_variant_items:
            item_min_qty = min(pricelist_variant_items, key=lambda i: i.min_quantity)
            min_qty = item_min_qty.min_quantity
            pricelist_tmpl_items = pricelist.item_ids.filtered(
                lambda i: i.product_tmpl_id.id == product.product_tmpl_id.id
                and i.min_quantity < min_qty
                and (not i.date_start or i.date_start <= today)
                and (not i.date_end or today <= i.date_end)
                and i.min_quantity > 0)
        else:
            pricelist_tmpl_items = pricelist.item_ids.filtered(
                lambda i: i.product_tmpl_id.id == product.product_tmpl_id.id
                and (not i.date_start or i.date_start <= today)
                and (not i.date_end or today <= i.date_end)
                and i.min_quantity > 0)
        self._prepare_dictionary(pricelist_variant_items, product, res)
        self._prepare_dictionary(pricelist_tmpl_items, product, res)
        res.sort(key=lambda i: i.get('min_qty', 0))
        return res

    def _prepare_dictionary(self, pricelist_items, product, res):
        for item in pricelist_items:
            final_price = item.fixed_price
            if item.compute_price == 'formula':
                price_limit = product.list_price
                price = (
                    product.list_price - (
                        (product.list_price * item.price_discount) / 100)
                )
                if item.price_round:
                    price = tools.float_round(
                        price, precision_rounding=item.price_round)
                if item.price_surcharge:
                    price += item.price_surcharge
                if item.price_min_margin:
                    price = max(price, price_limit + item.price_min_margin)
                if item.price_max_margin:
                    price = min(price, price_limit + item.price_max_margin)
                final_price = price
            elif item.compute_price == 'percentage':
                final_price = (
                    product.list_price - (product.list_price * item.percent_price) / 100
                )
            if final_price > 0:
                res.append({
                    "min_qty": item.min_quantity,
                    "price": final_price,
                    "currency": {
                        "position": product.currency_id.position,
                        "symbol": product.currency_id.symbol,
                    },
                })
