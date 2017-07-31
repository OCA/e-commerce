# -*- coding: utf-8 -*-
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class CheckoutSkipPayment(website_sale):

    @http.route()
    def payment(self, **post):
        if not request.website.checkout_skip_payment:
            return super(CheckoutSkipPayment, self).payment(**post)
        context = request.context
        order = request.website.sale_get_order(context=context)
        if order.force_quotation_send():
            # Clean context and session, then redirect to the confirmation page
            request.website.sale_reset(context=context)
            return request.redirect('/shop/confirmation')
        else:
            return request.render(
                'website_sale_skip_payment.confirmation_order_error')
