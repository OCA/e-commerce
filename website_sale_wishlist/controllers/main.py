# -*- coding: utf-8 -*-
# © 2016 Leonardo Donelli
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)

from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSaleWishlist(website_sale):

    def _get_or_create_wishlist_for_user(self, user_id):
        wishlist = request.env['wishlist'].search(
            [('user_id', '=', user_id)], limit=1)
        if not wishlist:
            wishlist = request.env['wishlist'].create(
                {'user_id': user_id})
        return wishlist

    @http.route()
    def cart_update(self, product_id, add_qty=0, set_qty=0, **kw):
        if kw.get('action', False) == 'move_to_wishlist':
            self.wishlist_update(product_id, **kw)
            add_qty = 0
            set_qty = -1
        return super(WebsiteSaleWishlist, self).cart_update(
            product_id, add_qty=add_qty, set_qty=set_qty, **kw)

    @http.route('/shop/wishlist', type='http', auth='user', website=True)
    def wishlist(self, **kwargs):
        return request.website.render('website_sale_wishlist.page')

    @http.route(['/shop/wishlist/update'], type='http', auth='user',
                methods=['POST'], website=True)
    def wishlist_update(self, product_id, **kw):
        wishlist = self._get_or_create_wishlist_for_user(request.env.uid)
        if kw.get('action', False) == 'remove':
            wishlist.remove_product(int(product_id))
        else:
            wishlist.add_product(int(product_id))
        return request.redirect("/shop/wishlist")
