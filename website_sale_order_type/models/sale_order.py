# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _cart_update(
            self, product_id=None, line_id=None, add_qty=0, set_qty=0,
            attributes=None, **kwargs):
        self.ensure_one()
        res = super(SaleOrder, self)._cart_update(
            product_id=product_id, line_id=line_id,
            add_qty=add_qty, set_qty=set_qty, attributes=attributes, **kwargs)
        if self.partner_id.sale_type:
            self.type_id = self.partner_id.sale_type
            self.onchange_type_id()
        self.match_order_type()
        return res
