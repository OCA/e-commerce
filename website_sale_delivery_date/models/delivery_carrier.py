# Copyright Cetmix OU 2025
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    DELAY_TYPE_SELECTION = [
        ("hours", "Hours"),
        ("days", "Days"),
    ]

    min_delivery_delay_type = fields.Selection(
        DELAY_TYPE_SELECTION,
        string="Minimum Delivery Delay Type",
        default="days",
        help="How to interpret the minimum delivery delay",
    )
    min_delivery_delay = fields.Float(
        string="Minimum Delivery Delay",
        default=1.0,
        help="Minimum delay between order placement and delivery",
    )
    weekday_rule_ids = fields.One2many(
        "delivery.weekday.rule",
        "carrier_id",
        string="Delivery Weekday Rules",
    )

    @api.constrains("min_delivery_delay")
    def _check_min_delivery_delay(self):
        for record in self:
            if record.min_delivery_delay < 0:
                raise ValidationError(_("Minimum delivery delay cannot be negative"))

    def get_delivery_constraints(self):
        self.ensure_one()
        now = fields.Datetime.now()

        # Calculate minimum delivery date
        if self.min_delivery_delay_type == "hours":
            min_date = now + timedelta(hours=self.min_delivery_delay)
        else:  # days
            min_date = now + timedelta(days=self.min_delivery_delay)
            min_date = min_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Calculate maximum delivery date (e.g., 30 days from now)
        max_date = now + timedelta(days=30)

        return {
            "visible": len(self.weekday_rule_ids) > 0,
            "min_date": min_date.strftime("%Y-%m-%d"),
            "max_date": max_date.strftime("%Y-%m-%d"),
        }

    def get_rule_by_weekday(self, dt):
        self.ensure_one()
        weekday = str(dt.weekday())
        return self.weekday_rule_ids.filtered(
            lambda r: r.weekday == weekday and r.active
        )
