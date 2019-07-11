# Copyright 2019 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale_stock.controllers.main import WebsiteSale
from odoo.http import request
from odoo import http


class WebsiteSale(WebsiteSale):
    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        # When user does a search in /shop the search input maintains
        # the value, so if you click on other category any product is listed.
        # This is a minor change that remove search keyword argument from keep
        # method.
        res = super(WebsiteSale, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post)
        attrib_list = request.httprequest.args.getlist('attrib')
        keep = QueryURL('/shop', category=category and int(category),
                        attrib=attrib_list, order=post.get('order'))
        res.qcontext['keep'] = keep
        return res
