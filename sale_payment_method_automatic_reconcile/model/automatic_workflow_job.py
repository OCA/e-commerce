# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
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

from openerp import models, api
from openerp.addons.sale_automatic_workflow import commit


class automatic_workflow_job(models.Model):
    _inherit = 'automatic.workflow.job'

    def _reconcile_invoices(self, cr, uid, ids=None, context=None):
        invoice_obj = self.pool.get('account.invoice')
        if ids is None:
            ids = invoice_obj.search(cr, uid,
                                     [('state', 'in', ['open'])],
                                     context=context)
        for invoice_id in ids:
            with commit(cr):
                invoice_obj.reconcile_invoice(cr, uid,
                                              [invoice_id],
                                              context=context)

    def run(self, cr, uid, ids=None, context=None):
        res = super(automatic_workflow_job, self).run(cr, uid, ids,
                                                      context=context)
        self._reconcile_invoices(cr, uid, context=context)
        return res
