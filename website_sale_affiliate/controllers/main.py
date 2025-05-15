# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
import logging

from odoo.http import request, route

from odoo.addons.website_sale.controllers.main import WebsiteSale as Base

_logger = logging.getLogger(__name__)


class WebsiteSale(Base):
    def _store_affiliate_info(self, **kwargs):
        affiliate = request.env["sale.affiliate"].sudo().find_from_kwargs(**kwargs)
        if not affiliate:
            return

        affiliate_request = affiliate.get_request(**kwargs)
        if not affiliate_request:
            return  # pragma: no cover

        request.session["affiliate_request"] = affiliate_request.id

    @route()
    def shop(self, *args, **post):
        res = super().shop(*args, **post)
        self._store_affiliate_info(**post)
        return res

    @route()
    def product(self, *args, **post):
        res = super().product(*args, **post)
        self._store_affiliate_info(**post)
        return res
