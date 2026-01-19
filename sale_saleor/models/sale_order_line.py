# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    saleor_order_line_id = fields.Char(
        string="Saleor Order Line ID", copy=False, index=True
    )
    saleor_fulfilled_qty = fields.Float(
        copy=False,
        default=0.0,
        help="Quantity already fulfilled in Saleor for this line.",
    )
