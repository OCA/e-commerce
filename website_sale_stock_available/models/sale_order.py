# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_free_qty(self, product):
        return super()._get_free_qty(
            product.with_context(website_sale_stock_available=True)
        )
