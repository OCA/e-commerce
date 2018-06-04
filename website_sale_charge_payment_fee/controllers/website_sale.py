# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.http import request
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleFee(WebsiteSale):

    @http.route()
    def payment(self, **post):
        res = super(WebsiteSaleFee, self).payment(**post)
        values = res.qcontext
        order = request.website.sale_get_order()
        payment_fee_id = post.get('payment_fee_id')
        if payment_fee_id or 'acquirers' in values:
            # If 'acquirers' in values, default behaviour when acquirers are
            # present, we update the order with the first one
            # (see 'payment' template)
            # If payment_fee_id, it means user selected it
            # (see website_sale_fee.js)
            if payment_fee_id:
                selected_acquirer = request.env[
                    'payment.acquirer'].browse(int(payment_fee_id))
                values['selected_acquirer'] = selected_acquirer
            else:
                selected_acquirer = values['acquirers'][0]
            order.sudo().update_fee_line(selected_acquirer.sudo())
            return request.render("website_sale.payment", values)
        return res
