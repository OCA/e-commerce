# -*- coding: utf-8 -*-

from odoo import fields, http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class WebsiteSale(WebsiteSale):

    @http.route()
    def product(self, product, category='', search='', **kwargs):
        """Add / update recently viewed products."""
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
        """Render recently viewed products."""
        records = request.env['website.sale.product.view'].search(
            [('sessionid', '=', request.session.sid)], limit=10)
        values = {'history': records}
        if kwargs.get('type') == 'popover':
            return request.render(
                'website_sale_recently_viewed_products.popover', values)
        return request.render(
            'website_sale_recently_viewed_products.page', values)
