# Copyright 2026 Domatix
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    delivery_note = fields.Text(
        related="sale_id.delivery_note",
        store=True,
    )
