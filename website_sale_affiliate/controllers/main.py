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
    def shop(
        self,
        page=0,
        category=None,
        search="",
        min_price=0.0,
        max_price=0.0,
        ppg=False,
        **post,
    ):
        res = super().shop(page, category, search, min_price, max_price, ppg, **post)
        self._store_affiliate_info(**post)
        return res

    @route()
    def product(self, product, category="", search="", **kwargs):
        res = super().product(product, category="", search="", **kwargs)
        self._store_affiliate_info(**kwargs)
        return res
