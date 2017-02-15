# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (http://www.serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import QueryURL, WebsiteSale


class WebsiteSale(WebsiteSale):

    @http.route(['/shop',
                 '/shop/page/<int:page>',
                 '/shop/category/<model("product.public.category"):category>',
                 """/shop/category/<model("product.public.category"):category>
                 /page/<int:page>""",
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
        brand_obj = request.env['product.brand']
        domain = []
        if post.get('search'):
            domain += [('name', 'ilike', post.get('search'))]
        brands = brand_obj.sudo().search(domain)
        keep = QueryURL('/page/product_brands', brand_id=[])
        values = {'brand_rec': brands, 'keep': keep}
        if post.get('search'):
            values.update({'search': post.get('search')})
        return http.request.render('website_sale_product_brand.product_brands',
                                   values)
