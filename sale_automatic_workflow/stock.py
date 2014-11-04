# -*- coding: utf-8 -*-
###############################################################################
#
#   sale_automatic_workflow for OpenERP
#   Copyright (C) 2011-TODAY Akretion <http://www.akretion.com>.
#     All Rights Reserved
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
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
from openerp.osv import orm, fields


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    _columns = {
        # if we add the column in stock.picking.out, we can't write it
        'workflow_process_id': fields.many2one('sale.workflow.process',
                                               'Sale Workflow Process'),
    }

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id,
                         context=None):
        # Read the correct journal for the shop company
        if not journal_id:
            journal_ids = self.pool.get('account.journal').search(
                cr, uid,
                [('type', '=', 'sale'),
                 ('company_id', '=', picking.sale_id.company_id.id)],
                limit=1)
            journal_id = journal_ids and journal_ids[0] or journal_id
        # Re-read partner with correct context to get the
        # correct accounts from properties
        if picking.sale_id:
            context = dict(context,
                           force_company=picking.sale_id.company_id.id,
                           company_id=picking.sale_id.company_id.id)
            picking = self.browse(cr, uid, picking.id, context=context)
            partner = self.pool.get('res.partner').browse(cr, uid,
                                                          partner.id,
                                                          context=context)
        invoice_vals = super(stock_picking, self)._prepare_invoice(
            cr, uid, picking, partner, inv_type, journal_id, context=context)
        base_picking = self.pool.get('stock.picking').browse(cr, uid,
                                                             picking.id,
                                                             context=context)
        if picking.sale_id:
            invoice_vals['currency_id'] =\
                picking.sale_id.pricelist_id.currency_id.id
            if base_picking.workflow_process_id.invoice_date_is_order_date:
                invoice_vals['date_invoice'] = picking.sale_id.date_order
            # Force period to avoid multi-company issues
            if not invoice_vals.get('period_id'):
                period_ids = self.pool.get('account.period').find(
                    cr, uid, invoice_vals.get('date_invoice', False),
                    context=context)
                invoice_vals['period_id'] =\
                    period_ids and period_ids[0] or False
        invoice_vals['workflow_process_id'] =\
            base_picking.workflow_process_id.id

        return invoice_vals

    def _prepare_shipping_invoice_line(self, cr, uid, picking, invoice, context=None):
        if context is None:
            context = {}
        if picking.sale_id:
            context = dict(context,
                           force_company=picking.sale_id.company_id.id,
                           company_id=picking.sale_id.company_id.id)
            picking = self.browse(cr, uid, picking.id, context=context)
        return super(stock_picking, self)._prepare_shipping_invoice_line(cr, uid, picking, invoice, context=context)

    def _prepare_invoice_line(self, cr, uid, group, picking, move_line,
                              invoice_id, invoice_vals, context=None):
        if picking.sale_id:
            context = dict(
                context,
                force_company=picking.sale_id.company_id.id,
                company_id=picking.sale_id.company_id.id)
            picking = self.browse(cr, uid, picking.id, context=context)
            move_line = self.pool.get('stock.move').browse(cr, uid,
                                                           move_line.id,
                                                           context=context)
        return super(stock_picking, self)._prepare_invoice_line(
            cr, uid, group, picking, move_line, invoice_id,
            invoice_vals, context=context)


class stock_picking_out(orm.Model):
    _inherit = "stock.picking.out"

    def validate_picking(self, cr, uid, ids, context=None):
        for picking in self.browse(cr, uid, ids, context=context):
            self.force_assign(cr, uid, [picking.id])
            partial_data = {}
            for move in picking.move_lines:
                partial_data["move" + str(move.id)] = {
                    'product_qty': move.product_qty,
                    'product_uom': move.product_uom.id,
                }
            self.do_partial(cr, uid, [picking.id], partial_data)
        return True
