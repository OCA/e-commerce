# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2014 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.addons.sale_automatic_workflow.automatic_workflow_job import (
    commit)


class PaymentMethod(orm.Model):
    _inherit = 'payment.method'

    _columns = {
        'days_before_cancel': fields.integer(
            'Days before cancel',
            help="After 'n' days, if the 'Import Rule' is not fulfilled, the "
                 "the sale order (or the import of the sale order) will "
                 "be canceled."),
    }

    _defaults = {
        'days_before_cancel': 90,
    }

    def _get_method_domain(self, cr, uid, context=None):
        return [
            ('days_before_cancel', '>', 0),
            ]

    def _get_sale_domain(self, cr, uid, method, context=None):
        min_date = datetime.now() - timedelta(days=method.days_before_cancel)
        min_date = min_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        return [
            ('state', '=', 'draft'),
            ('date_order', '<', min_date),
            ('payment_method_id', '=', method.id),
            ]

    def run_cancel_sale_order(self, cr, uid, context=None):
        order_obj = self.pool['sale.order']
        domain = self._get_method_domain(cr, uid, context=context)
        ids = self.search(cr, uid, domain, context=context)
        for method in self.browse(cr, uid, ids, context=context):
            sale_domain = self._get_sale_domain(
                cr, uid, method, context=context)
            order_ids = order_obj.search(
                cr, uid, sale_domain, context=context)
            _logger.debug('Cancel %s Sale Order for method %s'
                          % (len(order_ids), method.name))
            for order_id in order_ids:
                with commit(cr):
                    order_obj.action_cancel(
                        cr, uid, [order_id], context=context)
                    _logger.debug('Cancel Sale Order id : %s', order_id)
        return True
