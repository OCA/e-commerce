# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import http

from odoo.addons.website_quote.controllers.main import sale_quote


class SaleQuote(sale_quote):

    @http.route()
    def view(self, *args, **kwargs):
        response = super(SaleQuote, self).view(*args, **kwargs)
        transaction = http.request.env['payment.transaction'].sudo().browse(
            response.qcontext.get('tx_id'),
        )
        acquirer = transaction.acquirer_id
        response.qcontext.update({
            'tx_msg_help': acquirer.pre_msg,
            'tx_msg_pending': acquirer.pending_msg,
            'tx_msg_done': acquirer.done_msg,
            'tx_msg_cancel': acquirer.cancel_msg,
            'tx_msg_error': acquirer.error_msg,
        })
        return response
