# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.http import request, route
from odoo.addons.website_sale.controllers.main import QueryURL, WebsiteSale


class Wishlist(WebsiteSale):
    def _get_search_domain(self, *args, **kwargs):
        """Filter only wishlisted if requested so."""
        result = super(Wishlist, self)._get_search_domain(
            *args, **kwargs)
        if request.params.get("wishlist_only"):
            result.append(("id", "in",
                           request.website.wishlisted_product_template_ids()))
        return result

    @route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        """Let the view know we only want wishlisted products."""
        result = super(Wishlist, self).shop(
            page, category, search, ppg, **post)
        result.qcontext.update({
            "wishlist_only": bool(post.get("wishlist_only")),
            "keep": QueryURL(
                "/shop",
                attrib=post.get("attrib", list()),
                category=category and int(category),
                search=search,
                wishlist_only=post.get("wishlist_only"),
            ),
        })
        return result

    @route("/shop/wishlist/toggle/<model('product.template'):product>",
           type="json", auth="public", website=True)
    def wishlist_toggle(self, product):
        """Add a product to current session's wishlist.

        :return bool:
            Indicates if the product has been wishlisted or unwishlisted.
        """
        ProductWishlist = request.env["product.wishlist"]
        if product.wishlisted():
            ProductWishlist.search([
                ("id", "in", request.website.wishlist_product_ids()),
                ("product_tmpl_id", "in", product.ids),
            ]).unlink()
            return False
        else:
            ProductWishlist.create({
                "product_tmpl_id": product.id,
            })
            return True
