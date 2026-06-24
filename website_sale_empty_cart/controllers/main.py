# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleEmptyCart(WebsiteSale):
    @http.route("/shop/cart", type="http", auth="public", website=True, sitemap=False)
    def cart(self, access_token=None, revive="", **post):
        empty_cart = post.get("empty_cart")
        if empty_cart:
            order = request.website.sale_get_order()
            if order:
                order.order_line.unlink()
        return super().cart(
            access_token=access_token,
            revive=revive,
            **post,
        )
