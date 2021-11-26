# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.addons.website_sale.controllers.main import WebsiteSale


class SearchOrder(WebsiteSale):
    def _get_search_order(self, post):
        res = super(SearchOrder, self)._get_search_order(post)
        order_list = res.split(',')
        order_list.insert(
            order_list.index('website_published desc') + 1,
            'availability_sequence asc,availability_warning asc'
        )
        return ','.join(order_list)
