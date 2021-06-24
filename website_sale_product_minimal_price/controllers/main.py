# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
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
        product = request.env["product.product"].browse(product_id)
        pricelist = request.env["website"].get_current_website().get_current_pricelist()
        # Getting all min_quantity of the current product to compute the posible
        # price scale.
        qty_list = request.env["product.pricelist.item"].search([
            "|",
            ("product_id", "=", product.id),
            "|",
            ("product_tmpl_id", "=", product.product_tmpl_id.id),
            ("categ_id", "in", list(map(
                int, product.categ_id.parent_path.split('/')[0:-1]))),
            ("min_quantity", ">", 0),
        ]).mapped("min_quantity")
        qty_list = sorted(set(qty_list))
        res = []
        ctx = dict(request.env.context, pricelist=pricelist.id, quantity=0)
        last_price = product.with_context(ctx).price
        for min_qty in qty_list:
            ctx["quantity"] = min_qty
            new_price = product.with_context(ctx).price
            if new_price != last_price:
                res.append({
                    "min_qty": min_qty,
                    "price": new_price,
                    "currency": {
                        "position": product.currency_id.position,
                        "symbol": product.currency_id.symbol,
                    },
                })
                last_price = new_price
        return res
