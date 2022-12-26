# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
import logging

from odoo.http import request, route

from odoo.addons.website_sale.controllers.main import WebsiteSale as Base

_logger = logging.getLogger(__name__)


class WebsiteSale(Base):
    def _store_affiliate_info(self, **kwargs):
        Affiliate = request.env["sale.affiliate"]
        affiliate = Affiliate.sudo().find_from_kwargs(**kwargs)
        try:
            affiliate_request = affiliate.get_request(**kwargs)
            request.session["affiliate_request"] = affiliate_request.id
        except (AttributeError, ValueError) as err:
            _logger.info(err)

    @route()
    def shop(
        self,
        page=0,
        category=None,
        search="",
        min_price=0.0,
        max_price=0.0,
        ppg=False,
        **post
    ):
        res = super(WebsiteSale, self).shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            ppg=ppg,
            **post
        )
        self._store_affiliate_info(**post)
        return res

    @route()
    def product(self, product, category="", search="", **kwargs):
        res = super(WebsiteSale, self).product(
            product=product, category=category, search=search, **kwargs
        )
        self._store_affiliate_info(**kwargs)
        return res
