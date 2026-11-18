# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    resource_booking_timeout = fields.Float(
        "Pre-booking timeout",
        default=1,
        help=(
            "When resources are pre-booked, the booking will expire after "
            "this timeout if the quotation is not confirmed in time."
        ),
    )
    resource_booking_expiration = fields.Datetime(
        compute="_compute_resource_booking_expiration"
    )

    @api.depends("resource_booking_type_id", "resource_booking_timeout")
    def _compute_resource_booking_expiration(self):
        """When would the booking expire if placed right now."""
        self.resource_booking_expiration = False
        now = fields.Datetime.now()
        for one in self:
            if not one.resource_booking_type_id:
                continue
            one.resource_booking_expiration = now + timedelta(
                hours=one.resource_booking_timeout or 0
            )
