# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        vals = self._set_payment_term_id(vals)
        return super(SaleOrder, self).create(vals)

    @api.multi
    def write(self, vals):
        vals = self._set_payment_term_id(vals)
        return super(SaleOrder, self).write(vals)

    def _set_payment_term_id(self, vals):
        payment_acquirer_id = vals.get('payment_acquirer_id')
        payment_term_id = self.env['payment.acquirer'].browse(
            payment_acquirer_id).payment_term_id
        if not vals.get('payment_term_id') and payment_term_id:
            vals['payment_term_id'] = payment_term_id.id
        return vals
