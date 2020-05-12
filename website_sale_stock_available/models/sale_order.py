# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0,
                     set_qty=0, **kwargs):
        order = self.with_context(website_sale_stock_available=True)
        return super(SaleOrder, order)._cart_update(
            product_id, line_id, add_qty, set_qty, **kwargs)
