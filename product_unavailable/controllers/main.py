# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.addons.website_sale.controllers.main import WebsiteSale


class SearchOrder(WebsiteSale):
    def _get_search_order(self, post):
        return (
            'website_published desc,'
            'availability_sequence asc,'
            'availability_warning asc,'
            '%s,'
            'id desc'
        ) % post.get('order', 'website_sequence desc')
