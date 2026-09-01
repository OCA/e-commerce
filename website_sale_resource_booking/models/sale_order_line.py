# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _sync_resource_bookings(self):
        """On eCommerce, a draft SO produces pending/scheduled bookings."""
        result = super()._sync_resource_bookings()
        # Do not alter backend behavior
        for line in self.with_context(active_test=False):
            order = line.order_id
            # We only care about eCommerce orders
            if not order.website_id:
                continue
            bookings = line.resource_booking_ids
            # If paid, create missing partners
            if order.state == "sale":
                bookings.with_company(order.company_id.id)._confirm_prereservation()
                continue
            # Continue if it is not an eCommerce cart
            if (
                order.state != "draft"
                and order.env.context.get("website_id") == order.website_id.id
            ):
                continue
            # It is still a cart, so let's create pending bookings
            values = {
                "expiration": line.product_id.resource_booking_expiration,
                "sale_order_line_id": line.id,
                "type_id": line.product_id.resource_booking_type_id.id,
            }
            rbc_rel = line.product_id.resource_booking_type_combination_rel_id
            context = {
                "default_partner_id": line.order_id.partner_id.id,
                "default_combination_auto_assign": not rbc_rel,
                "default_combination_id": rbc_rel.combination_id.id,
            }
            # Assign prereservation data if user is logged in
            prereserved_partner = order.partner_id - order.website_id.user_id.partner_id
            if prereserved_partner:
                context.update(
                    {
                        "default_prereserved_name": prereserved_partner.name,
                        "default_prereserved_email": prereserved_partner.email,
                    }
                )
                # If an expired booking is being re-activated, we will update
                # the prereserved_* fields
                if any(not booking.active for booking in bookings):
                    values.update(
                        {
                            "prereserved_name": prereserved_partner.name,
                            "prereserved_email": prereserved_partner.email,
                        }
                    )
            # Add/remove bookings if needed
            self.env["resource.booking"]._cron_cancel_expired(
                [("id", "in", bookings.ids)]
            )
            expected_amount = int(line.product_uom_qty) if values["type_id"] else 0
            self.with_context(**context)._add_or_cancel_bookings(
                bookings, expected_amount, values
            )
        return result
