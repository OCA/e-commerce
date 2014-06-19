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

from openerp.osv import orm, fields


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'payment_method_id': fields.many2one(
            'payment.method', 'Payment Method', readonly=True,
            states={'draft': [('readonly', False)]}
        ),
    }

    def onchange_payment_method_id(self, cr, uid, ids, payment_method_id,
                                   type, partner_id, context=None):
        """Update account_id according to the account set on the payment_method
           else update account according to partner's receivable account
        """
        result = {}
        if type in ('out_invoice', 'out_refund'):
            if payment_method_id:
                payment_method = self.pool['payment.method'].\
                    browse(cr, uid, payment_method_id, context=context)
                if payment_method.receivable_account_id:
                    result = {'value': {
                        'account_id': payment_method.receivable_account_id.id
                        }
                    }
            if not result:
                p = self.pool['res.partner'].browse(cr, uid, partner_id)
                result = {'value': {
                    'account_id': p.property_account_receivable.id
                    }
                }
        return result

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,
                            date_invoice=False, payment_term=False,
                            partner_bank_id=False, company_id=False,
                            payment_method_id=False):
        """this override updates account_id according to the account set
           on payment_method
        """
        result = super(account_invoice, self).\
            onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice,
                                payment_term, partner_bank_id, company_id)
        if type in ('out_invoice', 'out_refund') and payment_method_id:
            payment_method = self.pool['payment.method'].\
                browse(cr, uid, payment_method_id)
            if payment_method.receivable_account_id:
                result['value']['account_id'] = \
                    payment_method.receivable_account_id.id
        return result
