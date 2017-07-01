# -*- coding: utf-8 -*-
# Copyright 2017 Specialty Medical Drugstore
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        price_qty_tiers = self.product_id.price_quantity_tiers[1]
        if len(price_qty_tiers) > 0:
            for line in self:
                price = 0
                exact_match = False
                for price_qty_tier in price_qty_tiers:
                    if price_qty_tier[0] == line.product_uom_qty:
                        price = price_qty_tier[0] * price_qty_tier[1]
                        exact_match = True
                        break
                if exact_match is False:
                    for i in range(0, len(price_qty_tiers)):
                        if line.product_uom_qty < price_qty_tiers[i][0]:
                            price_per_unit = price_qty_tiers[i-1][1]
                            price = line.product_uom_qty * price_per_unit
                            break
                taxes = line.tax_id.compute_all(
                    price/line.product_uom_qty,
                    line.order_id.currency_id,
                    line.product_uom_qty,
                    product=line.product_id,
                    partner=line.order_id.partner_id
                )
                line.update({
                    'price_tax':
                        (taxes['total_included'] - taxes['total_excluded']),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })
        else:
            return super(SaleOrderLine, self)._compute_amount()
