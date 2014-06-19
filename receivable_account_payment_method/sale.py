# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Romain Deheele
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Alter prepared values according to payment_method and
           possible default receivable account set on payment method
           Original function prepares the dict of values to create
           the new invoice for a sales order.

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        if context is None:
            context = {}
        invoice_vals = super(sale_order, self).\
            _prepare_invoice(cr, uid, order, lines, context=context)
        if order.payment_method_id:
            if order.payment_method_id.receivable_account_id:
                payment_method = order.payment_method_id
                invoice_vals.update({
                    'account_id': payment_method.receivable_account_id.id,
                    'payment_method_id': payment_method.id
                })
        return invoice_vals
