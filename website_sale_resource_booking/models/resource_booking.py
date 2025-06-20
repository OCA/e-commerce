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

    def _confirm_prereservation(self):
        """Convert prereservation data to actual partners, and confirm booking."""
        affected = self.with_context(dont_notify=True).filtered(
            lambda booking: booking.prereserved_name and booking.prereserved_email
        )
        for booking in affected:
            company_id = self.env.context.get(
                "force_company",
                self.env.user.company_id.id,
            )
            partner = self.env["res.partner"].search(
                [
                    ("email", "=ilike", booking.prereserved_email),
                    ("company_id", "in", [company_id, False]),
                ],
                limit=1,
            )
            if not partner:
                partner = self.env["res.partner"].create(
                    {
                        "name": booking.prereserved_name,
                        "email": booking.prereserved_email,
                        "company_id": company_id,
                    }
                )
            booking.partner_id = partner.id
            if booking.meeting_id:
                booking.meeting_id.name = booking._get_name_formatted(
                    booking.partner_id, booking.type_id
                )
        affected.write(
            {
                "expiration": False,
                # Partners are already created, so this data is irrelevant now
                "prereserved_email": False,
                "prereserved_name": False,
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

    def action_cancel(self):
        """Clean personal/cron data that you will never need again.

        Keeping this information without a clear purpose would incur into legal
        obligations in some countries, so it's better to just dump it.
        """
        self.write(
            {"prereserved_name": False, "prereserved_email": False, "expiration": False}
        )
        return super().action_cancel()
