# -*- coding: utf-8 -*-
import openerp.addons.website_sale.controllers.main as main
from openerp import http
from openerp.http import request


class WebsiteSale(main.website_sale):

    def cat_recursive_qty(self, categ, website_id):
        """if a category has no products and all it's children have no
            products remove it from the shop rendering altogether"""
        res = 0
        if not categ.published:
            # we are surely not intrested in it's children
            return res
        else:
            res += categ.get_product_qty_cat(website_id)
            if categ.child_id:
                # we need to fliter out unplblished again when travelling the
                # tree
                for child in categ.child_id.filtered(lambda x: x.published):
                    res += self.cat_recursive_qty(child, website_id)
        return res

    def _get_search_domain(self, search, category, attrib_values):
        if category:
            category = category.filtered('published')
        domain = super(WebsiteSale, self)._get_search_domain(
            search=search, category=category, attrib_values=attrib_values)
        return domain

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = main.PPG
        else:
            ppg = main.PPG
        result = super(WebsiteSale, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post)
        ws_id = http.request.website.id
        cat_qtys = {}
        ppc_model = request.env['product.public.category']
        # important, we calculate levels on all categories, because the
        # qcontext contains only the categories of the current level. The other
        # ones are just fetched recursivley via Child_ids
        # Precalculating them all may be inefficient. TODO: call it from the
        # qweb.
        for categ in ppc_model.search([('published', '=', True)]):
            cat_qtys[categ.id] = self.cat_recursive_qty(categ, ws_id)
        no_empty_cat_sorted = result.qcontext['categories'].filtered(
            lambda x: x.published).sorted(key=lambda x: x.sequence)
        result.qcontext.update({
            'categories': no_empty_cat_sorted,
            'cat_qtys': cat_qtys
        })
        return result
