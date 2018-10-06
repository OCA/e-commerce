# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class CheckoutSkipPayment(WebsiteSale):

    @http.route()
    def payment(self, **post):
        if not request.website.checkout_skip_payment:
            return super(CheckoutSkipPayment, self).payment(**post)
        order = request.website.sale_get_order()
        if order.force_quotation_send():
            # Clean session, then redirect to the confirmation page
            request.website.sale_reset()
            return request.redirect('/shop/confirmation')
        else:
            return request.render(
                'website_sale_skip_payment.confirmation_order_error')

    @http.route()
    def payment_get_status(self, sale_order_id, **post):
        # When skip payment step, the transaction not exists so only render
        # the waiting message in ajax json call
        if not request.website.checkout_skip_payment:
            return super(CheckoutSkipPayment, self).payment_get_status(
                sale_order_id, **post)
        return {
            'recall': True,
            'message': request.website._render(
                'website_sale_checkout_skip_payment.order_state_message'),
        }
