# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.addons.website_sale_charge_payment_fee.controllers.\
    website_sale import WebsiteSaleFee
from odoo.addons.website_sale_delivery.controllers.\
    main import WebsiteSaleDelivery


# to make python call WebsiteSaleFee before WebsiteSaleDelivery and compute
# payment fee line before the delivery one
class WebsiteSaleFeeDelivery(WebsiteSaleFee, WebsiteSaleDelivery):

    @http.route()
    def payment(self, **post):
        return super(WebsiteSaleFeeDelivery, self).payment(**post)
