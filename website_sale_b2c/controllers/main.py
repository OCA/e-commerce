# -*- coding: utf-8 -*-
# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp.http import request, route
from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSale(website_sale):
    def _enable_b2c_prices(self):
        """Enable B2C price mode if the user needs it."""
        if request.env.user.has_group(
                'website_sale_b2c.group_show_price_total'):
            request.context["b2c_prices"] = True
            del request.env  # To force recomputing it
            assert request.env.context.get("b2c_prices")
            if request.website_enabled:
                request.website = request.website.with_context(request.context)

    @route()
    def product(self, *args, **kwargs):
        self._enable_b2c_prices()
        return super(WebsiteSale, self).product(*args, **kwargs)

    @route()
    def shop(self, *args, **kwargs):
        self._enable_b2c_prices()
        return super(WebsiteSale, self).shop(*args, **kwargs)

    @route()
    def get_unit_price(self, *args, **kwargs):
        self._enable_b2c_prices()
        return super(WebsiteSale, self).get_unit_price(*args, **kwargs)
