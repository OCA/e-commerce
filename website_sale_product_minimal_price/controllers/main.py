# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http, fields
from odoo.http import request


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
        pricelist_items = pricelist.item_ids.filtered(
            lambda i: i.product_id == product
            and (not i.date_start or i.date_start <= today)
            and (not i.date_end or today <= i.date_end)
            and i.min_quantity > 0)
        pricelist_items = pricelist_items + pricelist.item_ids.filtered(
            lambda i: i.product_tmpl_id == product.product_tmpl_id
            and (not i.date_start or i.date_start <= today)
            and (not i.date_end or today <= i.date_end)
            and i.min_quantity > 0
            and (i.min_quantity < min(
                pricelist_items.mapped('min_quantity')) if pricelist_items else True))
        pricelist_items = pricelist_items + pricelist.item_ids.filtered(
            lambda i: i.categ_id.id in list(
                map(int, product.categ_id.parent_path.split('/')[0:-1]))
            and (not i.date_start or i.date_start <= today)
            and (not i.date_end or today <= i.date_end)
            and i.min_quantity > 0
            and (i.min_quantity < min(
                pricelist_items.mapped('min_quantity')) if pricelist_items else True))
        res = self._prepare_dictionary(pricelist_items, product, pricelist)
        res.sort(key=lambda i: i.get('min_qty', 0))
        return res

    def _prepare_dictionary(self, pricelist_items, product, pricelist):
        res = []
        for item in pricelist_items:
            ctx = dict(
                request.env.context, pricelist=pricelist.id, quantity=item.min_quantity)
            final_price = product.with_context(ctx).price
            res.append({
                "min_qty": item.min_quantity,
                "price": final_price,
                "currency": {
                    "position": product.currency_id.position,
                    "symbol": product.currency_id.symbol,
                },
            })
        return res
