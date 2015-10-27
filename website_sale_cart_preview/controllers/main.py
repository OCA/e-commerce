# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request

import openerp.addons.website_sale.controllers.main


class WebsiteSale(openerp.addons.website_sale.controllers.main.website_sale):

    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, **post):
        res = super(WebsiteSale, self).cart(**post)
        if post.get('type') == 'popover':
            # two qweb responses will be rendered in this case, the one by
            # super and this one, but there is no way around it if
            # we don't want to break inheritance
            return request.website.render(
                "website_sale_cart_preview.cart_popover", res.qcontext)
        return res
