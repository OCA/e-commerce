# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tests.common import Form


class ResourceBooking(models.Model):
    _inherit = "resource.booking"

    expiration = fields.Datetime(
        help=(
            "When will this booking expire if its related quotation is "
            "not confirmed in time?"
        )
    )

    # Temporary fields to avoid overloading database with res.partner records
    # for abandoned eCommerce carts
    prereserved_name = fields.Char()
    prereserved_email = fields.Char()

    def _compute_access_url(self):
        result = super()._compute_access_url()
        index = self.env.context.get("checkout_booking_index")
        if index and len(self) == 1:
            self.access_url = "/shop/booking/%d" % index
        return result

    def _update_expiration(self):
        """Update booking expiration."""
        # Only update if booking is altered from the website
        if not self.env.context.get("website_id"):
            return
        now = fields.Datetime.now()
        for one in self:
            # Only affects bookings related to sales
            if not one.sale_order_line_id:
                continue
            delta = timedelta(
                hours=one.sale_order_line_id.product_id.resource_booking_timeout
            )
            one.expiration = now + delta

    def _confirm_prereservation(self):
        """Convert prereservation data to actual partners, and confirm booking."""
        affected = self.with_context(dont_notify=True).filtered(
            lambda booking: booking.prereserved_name and booking.prereserved_email
        )
        for booking in affected:
            booking.partner_id = (
                self.env["res.partner"]
                .with_context(force_email=True)
                .find_or_create(
                    "{} <{}>".format(
                        booking.prereserved_name, booking.prereserved_email
                    )
                )
            )
            if booking.meeting_id:
                booking.meeting_id.name = booking._get_name_formatted(
                    booking.partner_id, booking.type_id
                )
        affected.write(
            {
                # Partners are already created, so this data is irrelevant now
                "prereserved_name": False,
                "prereserved_email": False,
                # Anti-smartypants safety belt: rotate security token now
                "access_token": False,
            }
        )
        # You're confirming some eCommerce sale, so confirm bookings directly
        affected.action_confirm()
        # Notify them
        for booking in affected:
            share_f = Form(
                self.env["portal.share"].with_context(
                    active_id=booking.id,
                    active_ids=booking.ids,
                    active_model=booking._name,
                    default_note=booking.requester_advice,
                    default_partner_ids=[(4, booking.partner_id.id, 0)],
                )
            )
            share = share_f.save()
            # Put invitations in mail queue
            share.with_context(
                mail_notify_force_send=False, mail_create_nosubscribe=True
            ).action_send_mail()

    @api.model
    def _cron_cancel_expired(self, domain=None):
        """Autocancel expired bookings."""
        domain = domain or []
        expired = self.with_context(no_mail_to_attendees=True).search(
            [
                ("expiration", "<", fields.Datetime.now()),
                ("state", "in", ("pending", "scheduled")),
            ]
            + domain
        )
        expired.action_cancel()
        # Cleaning personal data that you will never need again
        expired.write({"prereserved_name": False, "prereserved_email": False})

    @api.model_create_multi
    def create(self, vals_list):
        """Autosave default expiration date."""
        to_update_indexes = []
        for index, vals in enumerate(vals_list):
            if vals.get("start") and not vals.get("expiration"):
                to_update_indexes.append(index)
        result = super().create(vals_list)
        to_update_records = self.browse(prefetch=self._prefetch)
        for index in to_update_indexes:
            to_update_records |= result[index]
        to_update_records._update_expiration()
        return result

    def write(self, vals):
        """Autoupdate expiration date."""
        result = super().write(vals)
        if vals.get("start") and not vals.get("expiration"):
            self._update_expiration()
        return result
