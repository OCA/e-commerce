# © 2016 Serpent Consulting Services Pvt. Ltd. (http://www.serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    def _get_search_domain(self, search, category, attrib_values):
        domain = super(WebsiteSale, self)._get_search_domain(search, category,
                                                             attrib_values)
        if 'brand_id' in request.env.context:
            domain.append(
                ('product_brand_id', '=', request.env.context['brand_id']))
        return domain

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
        b_obj = request.env['product.brand']
        domain = [('website_published', '=', True)]
        if post.get('search'):
            domain += [('name', 'ilike', post.get('search'))]
        brand_rec = b_obj.sudo().search(domain)

        keep = QueryURL('/page/product_brands', brand_id=[])
        values = {'brand_rec': brand_rec,
                  'keep': keep}
        if post.get('search'):
            values.update({'search': post.get('search')})
        return request.render('website_sale_product_brand.product_brands',
                              values)
