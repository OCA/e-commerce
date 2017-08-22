# -*- coding: utf-8 -*-
# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # HACK Redefine computation or we cannot override it
    discounted_price = fields.Float(compute="_fnct_get_discounted_price")

    @api.model
    def _fnct_get_discounted_price(self):
        result = super(SaleOrderLine, self)._fnct_get_discounted_price(
            "discounted_price",
            None,
        )
        ProductTemplate = self.env["product.template"]
        for one in self:
            one.discounted_price = ProductTemplate._price_b2c_wrapper(
                one.with_context(quantity=one.product_uom_qty).product_id,
                {one.product_id.id: result[one.id]},
            )[one.product_id.id]
