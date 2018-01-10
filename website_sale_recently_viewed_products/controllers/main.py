# -*- coding: utf-8 -*-

from openerp import fields, http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSale(website_sale):

    @http.route()
    def product(self, product, category='', search='', **kwargs):
        record = request.env['website.sale.product.view'].search([
            ('sessionid', '=', request.session.sid),
            ('product_id', '=', product.id)
        ])
        if not record:
            record = request.env['website.sale.product.view'].create({
                'sessionid': request.session.sid,
                'product_id': product.id,
            })
        else:
            record.last_view_datetime = fields.Datetime.now()
        return super(WebsiteSale, self).product(product, category,
                                                search, **kwargs)

    @http.route(['/shop/recent'], type='http', auth='public', website=True)
    def recent(self, **kwargs):
        records = request.env['website.sale.product.view'].search(
            [('sessionid', '=', request.session.sid)], limit=10)
        values = {'history': records}
        if kwargs.get('type') == 'popover':
            return request.website.render(
                'website_sale_recently_viewed_products.popover', values)
        return request.website.render(
            'website_sale_recently_viewed_products.page', values)
