# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cart_update(self, *args, **kwargs):
        order = self.with_context(website_sale_stock_available=True)
        return super(SaleOrder, order)._cart_update(*args, **kwargs)
