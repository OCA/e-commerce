# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2012 Camptocamp SA
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

from osv import osv, fields


class reconcile_job(osv.osv):
    """
    Pool of invoices to auto-reconcile
    Workaround for bug:https://bugs.launchpad.net/openobject-server/+bug/961919
    As we cannot reconcile within action_invoice_create
    We have to postpone the reconcilation
    """

    _name = 'base.sale.auto.reconcile.job'

    _columns = {
        'invoice_id': fields.many2one('account.invoice',
                                      string='Invoice',
                                      select=True,
                                      required=True)
    }

    def create(self, cr, uid, vals, context=None):
        """
        Inherited to skip job creation if invoice_id
        already exists in the list.
        """
        if vals.get('invoice_id') and \
            not self.search(
                cr, uid, [('invoice_id', '=', vals['invoice_id'])]):
            # also call super() if no invoice_id is given in vals
            # in order to let pop the orm exception because this
            # is a required field
            return super(reconcile_job, self).create(
                cr, uid, vals, context=context)
        return False

    def run(self, cr, uid, ids=None, context=None):
        if ids is None:
            ids = self.search(cr, uid, [], context=context)
        inv_obj = self.pool.get('account.invoice')
        for job in self.browse(cr, uid, ids, context=context):
            invoice = job.invoice_id

            reconciled = False
            if not invoice.reconciled:
                reconciled = inv_obj.auto_reconcile_single(
                    cr, uid, invoice.id, context=context)

            # if the reconciliation have just been done
            # or it was already done, we drop the job
            if reconciled or invoice.reconciled:
                self.unlink(cr, uid, job.id, context=context)
            cr.commit()
        return True

reconcile_job()
