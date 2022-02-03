# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        """Update bookings partner when user creates account in checkout wizard."""
        result = super().onchange_partner_id()
        # Avoid sending calendar invites if user is in eCommerce checkout
        _self = self.with_context(dont_notify=True)
        for order in _self:
            # We only care about eCommerce orders
            if not order.website_id:
                continue
            for booking in order.resource_booking_ids:
                website_partner = order.website_id.partner_id
                if booking.partner_id != website_partner:
                    continue
                # Update partner if it was the public user (which is usually inactive)
                if booking.meeting_id:
                    booking.meeting_id.with_context(
                        active_test=False
                    ).partner_ids -= website_partner
                booking.partner_id = order.partner_id
        return result
