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
from tools.translate import _
from base_external_referentials.external_osv import ExternalSession
import os

class account_invoice(osv.osv):
    _inherit='account.invoice'
    
    def _export_one_resource(self, cr, uid, external_session, invoice_id, context=None):
        #TODO think about a better solution to pass the report_name
        context['report_name'] = self._send_invoice_report(cr, uid, external_session,
                                                             invoice_id, context=context)
        return super(account_invoice, self)._export_one_resource(cr, uid, external_session, 
                                                                    invoice_id, context=context)

    def _send_invoice_report(self, cr, uid, external_session, invoice_id, context=None):
        invoice = self.browse(cr, uid, invoice_id, context=context)
        invoice_number = invoice.number.replace('/', '-')
        invoice_path = self._get_invoice_path(cr, uid, external_session, invoice, context=context)
        if not external_session.sync_from_object.invoice_report:
            raise osv.except_osv(_("User Error"), _("You must define a report for the invoice for your sale shop"))
        report_name = "report.%s"%external_session.sync_from_object.invoice_report.report_name
        if not hasattr(external_session, 'file_session'):
            external_session.file_session = ExternalSession(
                                external_session.referential_id.ext_file_referential_id,
                                external_session.sync_from_object,
                                )
        return self.send_report(cr, uid, external_session.file_session, [invoice.id], report_name, 
                                                    invoice_number, invoice_path, context=context)

    def _get_invoice_path(self, cr, uid, external_session, invoice, context=None):
        ref_id = external_session.referential_id.id
        ext_partner_id = invoice.partner_id.get_extid(ref_id, context=context)
        ext_sale_id = invoice.sale_ids[0].get_extid(ref_id, context=context)
        if invoice.type == 'out_invoice':
            basepath = 'invoice'
        elif invoice.type == 'out_refund':
            basepath = 'creditmemo'
        return os.path.join(basepath, str(ext_partner_id), str(ext_sale_id))

