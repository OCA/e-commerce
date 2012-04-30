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
from osv import osv, fields
import os

class account_invoice(osv.osv):
    _inherit='account.invoice'
    
    _columns={
        'shop_id': fields.many2one('sale.shop', 'Shop', readonly=True, states={'draft': [('readonly', False)]}),
        'do_not_export': fields.boolean('Do not export',
                 help="This delivery order will not be exported to the external referential."),
    }
    
    def export_one_invoice(self, cr, uid, external_session, invoice_id, context=None):
        invoice = self.browse(cr, uid, invoice_id, context=context)
        invoice_number = invoice.number.replace('/', '-')
        invoice_path = self._get_invoice_path(cr, uid, external_session, invoice, context=context)
        report_name = "report.%s"%external_session.sync_from_object.invoice_report.report_name
        context['report_name'] = self.send_report(cr, uid, external_session, [invoice.id], report_name, invoice_number, invoice_path, context=context)
        #TODO think about a better solution to do get the report_name
        self._export_one_resource(cr, uid, external_session, invoice_id, context=context)
        return True

    def _get_invoice_path(self, cr, uid, external_session, invoice, context=None):
        ref_id = external_session.referential_id.id
        ext_partner_id = invoice.partner_id.get_extid(ref_id, context=context)
        ext_sale_id = invoice.sale_ids[0].get_extid(ref_id, context=context)
        if invoice.type == 'out_invoice':
            basepath = 'invoice'
        elif invoice.type == 'out_refund':
            basepath = 'creditmemo'
        return os.path.join(basepath, str(ext_partner_id), str(ext_sale_id))


    def _prepare_invoice_refund(self, cr, uid, ids, invoice_vals, date=None, period_id=None, description=None, journal_id=None, context=None):
        invoice = self.browse(cr, uid, invoice_vals['id'], context=context)
        invoice_vals = super(account_invoice, self)._prepare_invoice_refund(cr, uid, ids, invoice_vals, date=date, period_id=period_id, 
                                                    description=description, journal_id=journal_id, context=context)
        invoice_vals.update({
                'sale_ids': [(6,0, [sale.id for sale in invoice.sale_ids])],
                'shop_id': invoice.shop_id.id,
            })
        return invoice_vals
