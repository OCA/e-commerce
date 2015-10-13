    # -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   purchase_outillage for OpenERP                                            #
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

class purchase_order_line(Model):
    _inherit = "purchase.order.line"

    _columns = {
        'goodie_for_line_id': fields.many2one('purchase.order.line', 'Goodies for', help='The product linked to this goodie lines'),
        'goodies_line_ids': fields.one2many('purchase.order.line', 'goodie_for_line_id', 'Goodies linked', help=''),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context={}
        #TODO I should apply this only for automatic po need a read only mode
        if context.get("updated_from_op"):
            if not context.get('goodies_create_update'):
                ctx = context.copy()
                ctx['goodies_create_update'] = True
                for line in self.browse(cr, uid, ids, context=None):
                    if line.product_id.is_purchase_goodies(context=ctx):
                        vals['product_qty'] = self._get_new_qty_for_none_goodies_line(cr, uid, vals['product_qty'], line.product_id.id, line.order_id.id, context=ctx)
                    super(purchase_order_line, self).write(cr, uid, line.id, vals, context=ctx)
                    
                    qty_added = vals['product_qty'] - line.product_qty
                    for goodie in line.product_id.supplier_goodies_ids:
                        qty = goodie.get_quantity(qty_added, context=ctx)
                        po_line_for_goodie = False
                        for goodies_line in line.goodies_line_ids:
                            if goodies_line.product_id.id == goodie.linked_product_id.id:
                                po_line_for_goodie = goodies_line
                                break
                        #TODO manage correctly uom
                        print 'po_line_for_goodie', po_line_for_goodie
                        if po_line_for_goodie:
                            po_line_for_goodie.write({'product_qty': po_line_for_goodie.product_qty + qty}, context=ctx)
                        else:
                            self.create(cr, uid, 
                                    self._prepare_goodies_line(cr, uid, line.id, goodie, qty, line.order_id, line.date_planned, context=ctx),
                                    context=ctx)
                        self.update_none_goodies_line(cr, uid, qty, goodie.linked_product_id.id, line.order_id.id, context=ctx)
                return True
        return super(purchase_order_line, self).write(cr, uid, ids, vals, context=context)
    
    def create(self, cr, uid, vals, context=None):
        if context is None: context={}
        if not context.get('goodies_create_update'):
            ctx = context.copy()
            ctx['goodies_create_update'] = True
            product_obj = self.pool.get('product.product')
            product = product_obj.browse(cr, uid, vals['product_id'], context=ctx)
            
            if product.is_purchase_goodies(context=ctx):
                vals['product_qty'] = self._get_new_qty_for_none_goodies_line(cr, uid, vals['product_qty'], vals['product_id'], vals['order_id'], context=ctx)
            
            line_id = super(purchase_order_line, self).create(cr, uid, vals, context=context)
            
            order = self.pool.get('purchase.order').browse(cr, uid, vals['order_id'], context=context)
            for goodie in product.supplier_goodies_ids:
                qty = goodie.get_quantity(vals['product_qty'], context=ctx)
                self.create(cr, uid, 
                        self._prepare_goodies_line(cr, uid, line_id, goodie, qty, order, vals.get('date_planned'), context=ctx),
                        context=ctx)
                self.update_none_goodies_line(cr, uid, qty, goodie.linked_product_id.id, order.id, context=ctx)
            return line_id
        else:
            return super(purchase_order_line, self).create(cr, uid, vals, context=context)

    def _get_new_qty_for_none_goodies_line(self, cr, uid, qty, product_id, order_id, context=None):
        """If we want to buy X more product B we have to check if there is not already goodies
        line that containt this product. If yes we have to reduce the qty to buy by the the total
        of goodies lines
        :params qty float: quantity of product to buy
        :params product_id int: product id
        :params order_id: order id
        :return: the quantity for the none goodies line reduced by the quantity of goodies line
        :rtype: float
        """
        goodies_line_ids = self.search(cr, uid, [
                ['order_id', '=', order_id],
                ['product_id', '=', product_id],
                ['goodie_for_line_id', '!=', False]
            ], context=context)
        for goodie_line in self.browse(cr, uid, goodies_line_ids, context=context):
            qty -= goodie_line.product_qty
        if qty < 0:
            qty = 0
        return qty


    def update_none_goodies_line(self, cr, uid, goodies_qty, product_id, order_id, context=None):
        """Update the none line goodies, by this I mean :
        If you sold a product A with a goodies B
        If the scheduler have run a minimal rule for B before running the A rule.
        We have a line for the B product and we should remove the qty added by the goodies
        :params goodies_qty float: quantity of goodies product
        :params product_id int: product id
        :params order_id: order id
        :return: True
        :rtype: Boolean
        """
        product_line_id = self.search(cr, uid, [
                ['order_id', '=', order_id],
                ['product_id', '=', product_id],
                ['goodie_for_line_id', '=', False]
            ], context=context)
        if product_line_id:
            product_line = self.browse(cr, uid, product_line_id[0], context=context)
            new_qty = product_line.product_qty - goodies_qty
            if new_qty < 0: new_qty = 0
            product_line.write({'product_qty': new_qty}, context=context)
        return True


    def _prepare_goodies_line(self, cr, uid, line_id, goodie, qty, order, date_planned, context=None):
        """Prepare the purchase order line for goodies
        :params goodies browse_record: browse_record of product_links
        :params qty float: quantity of goodies to buy
        :params order browse_record: purchase order that contain this line
        :params schedule_date str: planned to for receiving the product
        :return: dictionnary of value for creating the purchase order line
        :rtype: dict
        """
        #TODO manage correctly uom
        acc_pos_obj = self.pool.get('account.fiscal.position')
        taxes_ids = goodie.product_id.supplier_taxes_id
        taxes = acc_pos_obj.map_tax(cr, uid, order.partner_id.property_account_position, taxes_ids)
        ctx = context.copy()
        #set the partner id in the context in order to have the good name for product
        ctx['partner_id'] = order.partner_id.id
        product = self.pool.get('product.product').browse(cr, uid, goodie.linked_product_id.id, context=ctx)
        return {
            'name': ">>>%s"%product.partner_ref,
            'product_qty': qty,
            'product_id': product.id,
            'product_uom': product.uom_po_id.id,
            'price_unit': goodie.cost_price or 0.0,
            'date_planned': date_planned,
            'notes': product.description_purchase,
            'taxes_id': [(6,0,taxes)],
            'order_id': order.id,
            'goodie_for_line_id': line_id
        }
