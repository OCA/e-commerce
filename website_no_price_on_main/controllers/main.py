# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
import openerp.addons.website_sale.controllers.main as website_sale_main


class WebsiteSale(website_sale_main.website_sale):

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        result = super(WebsiteSale, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post
        )
        result.qcontext.update({'is_main': request.website.is_main})
        return result

    @http.route()
    def product(self, product, category='', search='', **kwargs):
        result = super(WebsiteSale, self).product(
            product=product, category=category, search=search, **kwargs
        )
        result.qcontext.update({'is_main': request.website.is_main})
        return result

    @http.route()
    def cart(self, **post):
        result = super(WebsiteSale, self).cart(**post)
        result.qcontext.update({'is_main': request.website.is_main})
        return result

    @http.route()
    def confirm_order(self, **post):
        # write extra data on the sales order
        order = request.website.sale_get_order(context=request.context)
        if order:
            order.write({'customer_notes': post['customer_notes']})
        result = super(WebsiteSale, self).confirm_order(**post)
        return result

    @http.route()
    def checkout(self, **post):
        result = super(WebsiteSale, self).checkout(**post)
        result.qcontext.update({'is_main': request.website.is_main})
        return result

    @http.route()
    def payment(self, **post):
        order = request.website.sale_get_order()
        if request.website.is_main:
            if order:
                values = {'sale': order}
                order.write({'website_confirmed': True})
            # empty the session order before creating new one, also we must
            # bypass the search for the partner.last_website_so_id it does to
            # see if the user has a open draft. in the main website such memory
            # is not retained.
            partner = request.website.get_partner()
            partner.sudo().write({'last_website_so_id': None})
            request.session['sale_last_order_id'] = None
            request.session['sale_order_id'] = None
            request.session['sale_transaction_id'] = None
            return request.render(
                'website_no_price_on_main.confirm_quotation', values)
        # I cannot make non-main cart website_confirmed until payment done.
        # but when payment succeded the order is no more 'draft' so there is no
        # need!
        return super(WebsiteSale, self).payment(**post)
