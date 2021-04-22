# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"
    _sql_constraints = [
        (
            "sale_order_line_id_uniq",
            "UNIQUE(sale_order_line_id)",
            "A survey answer can be linked to only one sale order line.",
        )
    ]

    sale_order_line_id = fields.Many2one(
        "sale.order.line", string="Sale order line", index=True, ondelete="cascade"
    )
