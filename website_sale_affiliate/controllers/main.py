# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.http import request, route

from odoo.addons.website_sale.controllers.main import WebsiteSale as Base


class WebsiteSale(Base):
    def _store_affiliate_info(self, **kwargs):
        Affiliate = request.env["sale.affiliate"]
        affiliate = Affiliate.sudo().find_from_kwargs(**kwargs)
        if not affiliate:
            return

        affiliate_request = affiliate.get_request(**kwargs)
        if not affiliate_request:
            return  # pragma: no cover

        request.session["affiliate_request"] = affiliate_request.id

    @route()
    def shop(self, *args, **post):
        res = super(WebsiteSale, self).shop(*args, **post)
        self._store_affiliate_info(**post)
        return res

    @route()
    def product(self, *args, **kwargs):
        res = super(WebsiteSale, self).product(*args, **kwargs)
        self._store_affiliate_info(**kwargs)
        return res
