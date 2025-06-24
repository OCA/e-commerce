# Copyright Cetmix OU 2025
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DeliveryWeekdayRule(models.Model):
    _name = "delivery.weekday.rule"
    _description = "Delivery Weekday Rules for the carrier shipment availability"
    _order = "weekday, delivery_start_hour"

    WEEKDAY_SELECTION = [
        ("0", "Monday"),
        ("1", "Tuesday"),
        ("2", "Wednesday"),
        ("3", "Thursday"),
        ("4", "Friday"),
        ("5", "Saturday"),
        ("6", "Sunday"),
    ]

    name = fields.Char(compute="_compute_name", store=True)
    weekday = fields.Selection(
        WEEKDAY_SELECTION,
        required=True,
    )
    delivery_start_hour = fields.Float(
        required=True,
        help="When delivery starts on this day (e.g., 11.0 = 11:00).",
        digits=(16, 2),
    )
    delivery_end_hour = fields.Float(
        required=True,
        help="When delivery ends on this day",
        digits=(16, 2),
    )
    cutoff_hour = fields.Float(
        string="Cut-off Hour",
        help="If defined, cut-off for next-day delivery only. Works with "
        "min_delivery_delay_type = days.",
        digits=(16, 2),
    )
    carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Delivery Method",
        required=True,
        ondelete="cascade",
    )
    active = fields.Boolean(
        default=True,
        help="Whether this day is enabled for delivery",
    )
    create_uid = fields.Many2one(
        "res.users", string="Created by", default=lambda self: self.env.user
    )

    @api.depends("weekday", "delivery_start_hour", "delivery_end_hour")
    def _compute_name(self):
        for record in self:
            record.name = (
                f"{dict(self.WEEKDAY_SELECTION)[record.weekday]} "
                f"({record.delivery_start_hour:02.0f}:00 - "
                f"{record.delivery_end_hour:02.0f}:00)"
            )

    @api.constrains("delivery_start_hour", "delivery_end_hour", "cutoff_hour")
    def _check_start_and_end_hour(self):
        for record in self:
            weekday_name = dict(self.WEEKDAY_SELECTION)[record.weekday]
            if record.delivery_start_hour < 0 or record.delivery_start_hour >= 24:
                raise ValidationError(
                    _(
                        "%(weekday)s: Delivery start hour must be between 0 and 24",
                        weekday=weekday_name,
                    )
                )
            if record.delivery_end_hour < 0 or record.delivery_end_hour > 24:
                raise ValidationError(
                    _(
                        "%(weekday)s: Delivery end hour must be between 0 and 24",
                        weekday=weekday_name,
                    )
                )
            if record.delivery_start_hour >= record.delivery_end_hour:
                raise ValidationError(
                    _(
                        "%(weekday)s: The delivery start hour "
                        "must be before the delivery end hour",
                        weekday=weekday_name,
                    )
                )
            if record.cutoff_hour and (
                record.cutoff_hour < 0 or record.cutoff_hour >= 24
            ):
                raise ValidationError(
                    _(
                        "%(weekday)s: Cut-off hour must be between 0 and 24",
                        weekday=weekday_name,
                    )
                )
