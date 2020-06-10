# Copyright 2020 Tecnativa - Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import QueryURL


class WebsiteSale(WebsiteSale):
    def _get_search_domain(self, search, category, attrib_values):
        domain = super()._get_search_domain(search, category, attrib_values)
        price_vals = request.context.get("price_vals")
        if price_vals:
            to_add = []
            if price_vals[0] is not None:
                to_add += [
                    ("list_price", ">=", price_vals[0])
                ]
            if price_vals[1] is not None:
                to_add += [
                    ("list_price", "<=", price_vals[1])
                ]
            if len(to_add) == 2:
                to_add.insert(0, '&')
            domain += to_add
        return domain

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        # User values
        try:
            custom_min_price = float(post.get("min_price"))
        except (ValueError, TypeError):
            custom_min_price = None
        try:
            custom_max_price = float(post.get("max_price"))
        except (ValueError, TypeError):
            custom_max_price = None
        # Call Super with context
        if custom_max_price is not None and custom_min_price is not None:
            # Sanitize Values
            if custom_min_price > custom_max_price:
                custom_max_price, custom_min_price = custom_min_price, custom_max_price
        request.context = dict(
            request.context,
            price_vals=[custom_min_price, custom_max_price])
        response = super().shop(
            page=page, category=category, search=search, ppg=ppg, **post
        )
        # Search maximum price
        # Using pricelist in this way to follow Odoo implementation
        _pricelist_context, pricelist = self._get_pricelist_context()
        request.context = dict(
            request.context,
            pricelist=pricelist.id,
            partner=request.env.user.partner_id,
            price_vals=None)
        product_id = request.env['product.template'].with_context(
            prefetch_fields=False
        ).search(
            self._get_search_domain(
                search,
                category,
                response.qcontext.get('attrib_values')),
            order='list_price DESC', limit=1)
        max_price = product_id.list_price
        # Price Filter QWeb Values
        keep = QueryURL(
            '/shop',
            category=category and int(category),
            search=post.get('search'),
            attrib=post.get('atrib'),
            order=post.get('order'),
            min_price=custom_min_price,
            max_price=custom_max_price)
        response.qcontext.update({
            "custom_min_price": custom_min_price,
            "custom_max_price": custom_max_price,
            "max_price": max_price,
            "keep": keep,
        })
        return response
