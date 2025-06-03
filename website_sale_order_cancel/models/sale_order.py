# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    can_cancel = fields.Boolean(
        compute="_compute_can_cancel",
    )

    @api.depends("commitment_date", "expected_date", "state")
    def _compute_can_cancel(self):
        cancel_restrict_days = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale.cancel_restrict_days", default=1)
        )
        today = fields.Date.today()
        for order in self:
            if order.state in ["sale", "done"]:
                scheduled_date = order.commitment_date or order.expected_date
                if scheduled_date:
                    restriction_date = (
                        scheduled_date - timedelta(days=cancel_restrict_days)
                    ).date()
                    order.can_cancel = today <= restriction_date
                else:
                    order.can_cancel = False
            else:
                order.can_cancel = False
