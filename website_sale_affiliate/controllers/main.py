# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.addons.website_sale.controllers.main import WebsiteSale as Base
from odoo.http import request, route


class WebsiteSale(Base):
    def _store_affiliate_info(self, **kwargs):
        Affiliate = request.env['sale.affiliate']
        affiliate = Affiliate.sudo().find_from_kwargs(**kwargs)
        try:
            affiliate_request = affiliate.get_request(**kwargs)
            request.session['affiliate_request'] = affiliate_request.id
        except (AttributeError, ValueError):
            pass

    @route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        res = super(WebsiteSale, self).shop(page, category,
                                            search, ppg, **post)
        self._store_affiliate_info(**post)
        return res

    @route()
    def product(self, product, category='', search='', **kwargs):
        res = super(WebsiteSale, self).product(product, category='',
                                               search='', **kwargs)
        self._store_affiliate_info(**kwargs)
        return res
