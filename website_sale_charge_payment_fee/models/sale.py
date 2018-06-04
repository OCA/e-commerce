# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def update_fee_line(self, acquirer):
        for line in self.order_line:
            if line.payment_fee_line:
                line.unlink()
        if acquirer.charge_fee:
            if acquirer.charge_fee_type == 'fixed':
                price = acquirer.charge_fee_fixed_price
                if (
                    self.company_id.currency_id.id !=
                    self.pricelist_id.currency_id.id
                ):
                    price = self.company_id.currency_id.with_context(
                        date=self.date_order
                    ).compute(price, self.pricelist_id.currency_id)
            elif acquirer.charge_fee_type == 'percentage':
                price = (
                    acquirer.charge_fee_percentage / 100.0
                ) * self.amount_total
            self.env['sale.order.line'].create({
                'order_id': self.id,
                'payment_fee_line': True,
                'product_id': acquirer.charge_fee_product_id.id,
                'product_uom': acquirer.charge_fee_product_id.uom_id.id,
                'name': acquirer.charge_fee_description,
                'price_unit': price,
                'product_uom_qty': 1,
                'tax_id': [
                    (6, 0, [t.id for t in acquirer.charge_fee_tax_ids])
                ],
            })


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    payment_fee_line = fields.Boolean("Payment fee line", readonly=True)
