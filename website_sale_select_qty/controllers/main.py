# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleSelectQty(WebsiteSale):

    @http.route()
    def product(self, *args, **kwargs):
        response = super(WebsiteSaleSelectQty, self).product(*args, **kwargs)

        try:
            quantity = float(request.params['quantity'])
            quantity = '%g' % quantity
        except (KeyError, ValueError):
            quantity = '1'

        response.qcontext['quantity'] = quantity
        return response
