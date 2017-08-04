# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
import logging

from odoo.http import request, route
from odoo.addons.website_sale.controllers.main import WebsiteSale as Base

_logger = logging.getLogger(__name__)


class WebsiteSale(Base):
    @route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        affiliate_id = post.get('ref')
        if affiliate_id:
            try:
                request.session['affiliate_id'] = int(affiliate_id)
                request.session['affiliate_key'] = post.get('key')
            except ValueError:
                _logger.debug('Invalid affiliate ID value')
        return super(WebsiteSale, self).shop(page, category,
                                             search, ppg, **post)
