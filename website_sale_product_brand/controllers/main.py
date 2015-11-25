# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services Pvt. Ltd.
#                                     (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp import http
from openerp.http import request
from openerp import SUPERUSER_ID
from openerp.addons.website_sale.controllers.main import QueryURL
from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSale(website_sale):

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
            request.context.setdefault('brand_id', int(brand))
        result = super(WebsiteSale, self).shop(page=page, category=category,
                                               brand=brand, search=search,
                                               **post)
        result.qcontext['brand'] = brand
        return result

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
