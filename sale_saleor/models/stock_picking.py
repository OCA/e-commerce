# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        res = super()._action_done()

        # After pickings are marked done, auto-trigger fulfill for
        # corresponding Saleor orders. The sale.order helper will
        # compute how much is newly delivered and only fulfill that
        # delta (supports both partial and full deliveries).
        sale_orders = self.mapped("sale_id").filtered("saleor_order_id")
        for order in sale_orders:
            try:
                # Delegate the actual API/job call to the sale.order helper
                order._saleor_auto_fulfill()
            except Exception:
                # Never block stock flow because of Saleor issues
                continue

        return res
