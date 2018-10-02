# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models, api


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    @api.multi
    def get_price_available(self, order):
        with self.env.do_in_draft():
            payment_fee_line = order.order_line.filtered('payment_fee_line')
            if payment_fee_line:
                # set as delivery line in draft mode, to exclude it from the
                # computation of order total, used to compute delivery fee
                payment_fee_line.is_delivery = True
            res = super(DeliveryCarrier, self).get_price_available(order)
        return res
