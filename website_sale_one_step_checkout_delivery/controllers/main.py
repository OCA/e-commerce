# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import http
from odoo.addons.website_sale_one_step_checkout.controllers.main import \
    WebsiteSale
from odoo.http import request


class WebsiteSaleOneStepCheckoutDelivery(WebsiteSale):

    @http.route(['/shop/checkout/change_delivery'], type='json', auth="public",
                website=True, multilang=True)
    def change_delivery(self, **post):
        """If delivery method was changed in frontend.

        Change and apply delivery carrier / amount to sale order.
        """
        order = request.website.sale_get_order()
        carrier_id = int(post.get('carrier_id'))

        return self.do_change_delivery(order, carrier_id)

    def do_change_delivery(self, order, carrier_id):
        """Apply delivery amount to current sale order."""
        if not order or not carrier_id:
            return {'success': False}

        # order_id is needed to get delivery carrier price
        if not request.context.get('order_id'):
            context = dict(request.context)
            context.update({'order_id': order.id})

        # generate updated total prices
        updated_order = request.website.sale_get_order()
        updated_order._check_carrier_quotation(force_carrier_id=carrier_id)
        updated_order.delivery_set()

        result = {
            'success': True,
            'order_total': updated_order.amount_total,
            'order_total_taxes': updated_order.amount_tax,
            'order_total_delivery': updated_order.amount_delivery
        }

        return result
