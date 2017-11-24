# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (http://www.serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import http
from openerp.http import request
from openerp import SUPERUSER_ID
from openerp.addons.website_sale.controllers.main import QueryURL
from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSale(website_sale):

    @http.route(['/shop',
                 '/shop/page/<int:page>',
                 '/shop/category/<model("product.public.category"):category>',
                 '/shop/category/<model("product.public.category"):category'
                 '>/page/<int:page>',  # Continue previous line
                 '/shop/brands'],
                type='http',
                auth='public',
                website=True)
    def shop(self, page=0, category=None, brand=None, search='', **post):
        if brand:
            context = dict(request.env.context)
            context.setdefault('brand_id', int(brand))
            request.env.context = context
        return super(WebsiteSale, self).shop(page=page, category=category,
                                             brand=brand, search=search,
                                             **post)

    # Method to get the brands.
    @http.route(
        ['/page/product_brands'],
        type='http',
        auth='public',
        website=True)
    def product_brands(self, **post):
        cr, context, pool = (request.cr,
                             request.context,
                             request.registry)
        b_obj = pool['product.brand']
        domain = []
        if post.get('search'):
            domain += [('name', 'ilike', post.get('search'))]
        brand_ids = b_obj.search(cr, SUPERUSER_ID, domain)
        brand_rec = b_obj.browse(cr, SUPERUSER_ID, brand_ids, context=context)

        keep = QueryURL('/page/product_brands', brand_id=[])
        values = {'brand_rec': brand_rec,
                  'keep': keep}
        if post.get('search'):
            values.update({'search': post.get('search')})
        return request.website.render(
            'website_sale_product_brand.product_brands',
            values)
