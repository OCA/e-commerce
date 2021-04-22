# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _lines_pending_survey(self):
        """Get sale order lines with pending survey answers."""
        result = self.env['sale.order.line']
        for line in self.mapped("order_line"):
            if not line.product_id.survey_id:
                continue
            if line.survey_user_input_ids.state != "done":
                result |= line
        return result
