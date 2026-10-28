# Copyright 2026 CIT Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

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
        now = fields.Datetime.now()
        for product in self:
            if not product.resource_booking_type_id:
                product.resource_booking_expiration = False
            else:
                product.resource_booking_expiration = now + timedelta(
                    hours=product.resource_booking_timeout or 0
                )
