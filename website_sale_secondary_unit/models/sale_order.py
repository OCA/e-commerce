# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.http import request
from odoo.tools.float_utils import float_round


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _cart_find_product_line(self, product_id=None, line_id=None, **kwargs):
        """
        Search sale order lines with secondary units
        """
        so_lines = super()._cart_find_product_line(
            product_id=product_id, line_id=line_id, **kwargs)
        if so_lines:
            if line_id:
                sol = self.env['sale.order.line'].browse(line_id)
                secondary_uom_id = sol.secondary_uom_id.id
            else:
                secondary_uom_id = self.env.context.get(
                    'secondary_uom_id', False)
            so_lines = so_lines.filtered(
                lambda x: x.secondary_uom_id.id == secondary_uom_id)
        return so_lines

    @api.multi
    def _website_product_id_change(self, order_id, product_id, qty=0):
        res = super()._website_product_id_change(
            order_id, product_id, qty=qty)
        secondary_uom_id = self.env.context.get('secondary_uom_id', False)
        res['secondary_uom_id'] = secondary_uom_id
        return res

    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0,
                     attributes=None, **kwargs):
        if line_id:
            sol = self.env['sale.order.line'].browse(line_id)
            secondary_uom_id = sol.secondary_uom_id.id
        else:
            secondary_uom_id = request.session.get('secondary_uom_id', False)
        ctx = self.env.context.copy()
        if secondary_uom_id:
            ctx['secondary_uom_id'] = secondary_uom_id
        res = super(SaleOrder, self.with_context(ctx))._cart_update(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            attributes=attributes, **kwargs)
        return res

    def _compute_cart_info(self):
        super(SaleOrder, self)._compute_cart_info()
        for order in self:
            secondary_unit_lines = order.website_order_line.filtered(
                'secondary_uom_id')
            if secondary_unit_lines:
                cart_secondary_quantity = int(sum(
                    secondary_unit_lines.mapped('secondary_uom_qty')))
                so_lines = order.website_order_line - secondary_unit_lines
                cart_quantity = int(sum(so_lines.mapped('product_uom_qty')))
                order.cart_quantity = cart_quantity + cart_secondary_quantity


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def create(self, vals):
        SecondaryUom = self.env['product.secondary.unit']
        secondary_uom = SecondaryUom.browse(
            vals.get('secondary_uom_id', False))
        product_uom = self.env['product.uom'].browse(vals['product_uom'])
        if secondary_uom:
            factor = secondary_uom.factor * product_uom.factor
            vals['secondary_uom_qty'] = float_round(
                vals['product_uom_qty'] / (factor or 1.0),
                precision_rounding=secondary_uom.uom_id.rounding
            )
        return super(SaleOrderLine, self).create(vals)

    def write(self, vals):
        SecondaryUom = self.env['product.secondary.unit']
        for line in self:
            secondary_uom = ('secondary_uom_id' in vals and
                             SecondaryUom.browse(vals['secondary_uom_id']) or
                             line.secondary_uom_id)
            if 'product_uom_qty' in vals and secondary_uom:
                factor = secondary_uom.factor * vals.get(
                    'product_uom', line.product_uom.factor)
                vals['secondary_uom_qty'] = float_round(
                    vals['product_uom_qty'] / (factor or 1.0),
                    precision_rounding=secondary_uom.uom_id.rounding
                )
        return super(SaleOrderLine, self).write(vals)
