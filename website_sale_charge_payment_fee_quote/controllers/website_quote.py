# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.http import request
from odoo.addons.website_quote.controllers.main import sale_quote


class sale_quote_fee(sale_quote):

    @http.route()
    def view(self, order_id, pdf=None, token=None, message=False, **post):
        res = super(sale_quote_fee, self).view(
            order_id, pdf=pdf, token=token, message=message, **post)
        if res.template == 'website_quote.so_quotation':
            values = res.qcontext
            order = values['quotation']
            if order.state in ['draft', 'sent']:
                payment_fee_id = post.get('payment_fee_id')
                if payment_fee_id or 'acquirers' in values:
                    # see website_sale_charge_payment_fee controller
                    if payment_fee_id:
                        selected_acquirer = request.env[
                            'payment.acquirer'].browse(int(payment_fee_id))
                        values['selected_acquirer'] = selected_acquirer
                    else:
                        selected_acquirer = values['acquirers'][0]
                    order.sudo().update_fee_line(selected_acquirer.sudo())
                    return request.render("website_quote.so_quotation", values)
        return res
