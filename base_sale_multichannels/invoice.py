# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   base_sale_multichannels for OpenERP                                       #
#   Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>  #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################
from openerp.osv.orm import Model
from openerp.osv import fields

class account_invoice(Model):
    _inherit='account.invoice'
    
    _columns={
        'shop_id': fields.many2one('sale.shop', 'Shop', readonly=True, states={'draft': [('readonly', False)]}),
        'do_not_export': fields.boolean('Do not export',
                 help="This delivery order will not be exported to the external referential."),
    }

    def _prepare_invoice_refund(self, cr, uid, ids, invoice_vals, date=None, period_id=None, description=None, journal_id=None, context=None):
        invoice = self.browse(cr, uid, invoice_vals['id'], context=context)
        invoice_vals = super(account_invoice, self)._prepare_invoice_refund(cr, uid, ids, invoice_vals, date=date, period_id=period_id, 
                                                    description=description, journal_id=journal_id, context=context)
        invoice_vals.update({
                'sale_ids': [(6,0, [sale.id for sale in invoice.sale_ids])],
                'shop_id': invoice.shop_id.id,
            })
        return invoice_vals
