# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
import logging

from odoo.http import request, route
from odoo.addons.website_sale.controllers.main import WebsiteSale as Base

_logger = logging.getLogger(__name__)


class WebsiteSale(Base):
    def _store_affiliate_info(self, **kwargs):
        try:
            request.session['affiliate_id'] = int(kwargs['ref'])
            try:
                request.session['affiliate_key'] = kwargs['key']
            except KeyError:
                request.session.pop('affiliate_key', None)
        except KeyError:
            pass
        except ValueError:
            _logger.debug('Invalid affiliate ID value')

    @route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        self._store_affiliate_info(**post)
        return super(WebsiteSale, self).shop(page, category,
                                             search, ppg, **post)

    @route()
    def product(self, product, category='', search='', **kwargs):
        _logger.warning(request.session)
        self._store_affiliate_info(**kwargs)
        return super(WebsiteSale, self).product(product, category='',
                                                search='', **kwargs)
