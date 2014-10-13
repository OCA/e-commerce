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

from openerp.osv import orm
from openerp.addons.sale_automatic_workflow.automatic_workflow_job import (
    commit)


class AutomaticWorkflowJob(orm.Model):
    _inherit = 'automatic.workflow.job'

    def _get_domain_for_sale_reservation(self, cr, uid, context=None):
        return [
            ('order_id.state', '=', 'draft'),
            ('order_id.workflow_process_id.reserve_sale_order', '=', True),
            ('reservation_ids', '=', False),
        ]

    def _get_reservable_line(self, cr, uid, context=None):
        line_obj = self.pool['sale.order.line']
        domain = self._get_domain_for_sale_reservation(
            cr, uid, context=context)
        return line_obj.search(cr, uid, domain, context=context)

    def _prepare_reserve_wizard(self, cr, uid, context=None):
        return {}

    def _reserve_sale_order(self, cr, uid, context=None):
        reserve_obj = self.pool['sale.stock.reserve']
        vals = self._prepare_reserve_wizard(cr, uid, context=context)
        reserve_id = reserve_obj.create(cr, uid, vals, context=context)
        line_ids = self._get_reservable_line(cr, uid, context=context)
        for line_id in line_ids:
            with commit(cr):
                reserve_obj.stock_reserve(
                    cr, uid, [reserve_id], [line_id], context=context)

    def run(self, cr, uid, ids=None, context=None):
        """ Must be called from ir.cron """
        super(AutomaticWorkflowJob, self).run(
            cr, uid, ids, context=context)
        self._reserve_sale_order(cr, uid, context=context)
        return True
