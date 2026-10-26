# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timezone
from urllib.parse import quote_plus

from dateutil.parser import isoparse

from odoo import _
from odoo.exceptions import ValidationError
from odoo.http import request, route

from ...website_sale.controllers import main


class WebsiteSale(main.WebsiteSale):
    def _get_bookings(self):
        """Obtain bookings from current cart."""
        order = request.website.sale_get_order()
        order = order.with_context(active_test=False)
        return order.mapped("order_line.resource_booking_ids")

    def _get_indexed_booking(self, index):
        """Get indexed booking from current cart.

        :param int index: 1 is the 1st element.
        """
        bookings = self._get_bookings().sorted("id")
        if index > len(bookings):
            raise IndexError()
        return bookings[index - 1]

    def _booking_redirection(self, booking, index):
        """Call this method in /schedule and /confirm to redirect if
        the booking has expired.
        """
        if not booking.active:
            msg = _("Booking has expired")
            url = f"/shop/booking/{index}/schedule?error={quote_plus(msg)}"
            booking.sale_order_line_id._sync_resource_bookings()  # re-active
            return request.redirect(url)

    def _check_cart(self, order_sudo):
        """Redirect to scheduling bookings if still not done."""
        order_sudo.order_line._sync_resource_bookings()
        bookings = order_sudo.mapped("order_line.resource_booking_ids").filtered(
            lambda r: r.state == "pending"
        )
        if bookings:
            return request.redirect("/shop/booking/1/schedule")
        return super()._check_cart(order_sudo)

    @route(
        [
            "/shop/booking/<int:index>/schedule",
            "/shop/booking/<int:index>/schedule/<int:year>/<int:month>",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def booking_schedule(self, index, year=None, month=None, error=None, **post):
        """Schedule pending bookings."""
        # Proceed to checkout if there are no bookings in this cart
        bookings = self._get_bookings().with_context(checkout_booking_index=index)
        if not bookings:
            return request.redirect("/shop/checkout")
        # Proceed to checkout if we passed the last booking
        try:
            booking = self._get_indexed_booking(index).with_context(
                checkout_booking_index=index
            )
        except IndexError:
            return request.redirect("/shop/checkout")
        redirection = self._booking_redirection(booking, index)
        if redirection:
            return redirection
        count = len(bookings)
        values = booking.with_context(
            tz=booking.type_id.resource_calendar_id.tz
        )._get_calendar_context(year, month)
        values.update(
            {
                "booking_index": index,
                "bookings_count": count,
                "error": error,
                "website_sale_order": request.website.sale_get_order(),
                "wizard_title": _("Pre-schedule your booking (%(index)d of %(total)d)")
                % {"index": index, "total": count},
            }
        )
        return request.render("website_sale_resource_booking.scheduling", values)

    @route(
        ["/shop/booking/<int:index>/confirm"],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def booking_confirm(self, index, partner_name, partner_email, when, **post):
        """Pre-reserve resource booking."""
        booking_sudo = (
            self._get_indexed_booking(index)
            .sudo()
            .with_context(
                # Avoid calendar notifications now, SO is still draft
                dont_notify=True,
                no_mail_to_attendees=True,
            )
        )
        if not booking_sudo:
            return request.redirect("/shop/checkout")
        redirection = self._booking_redirection(booking_sudo, index)
        if redirection:
            return redirection
        when_tz_aware = isoparse(when)
        when_naive = when_tz_aware.astimezone(timezone.utc).replace(tzinfo=None)
        try:
            booking_sudo.start = when_naive
        except ValidationError as error:
            url = f"/shop/booking/{index}/schedule?error={quote_plus(str(error))}"
            return request.redirect(url)
        # Store partner info to autocreate and autoconfirm later
        product = booking_sudo.sale_order_line_id.product_id
        booking_sudo.write(
            {
                "expiration": product.resource_booking_expiration,
                "prereserved_email": partner_email,
                "prereserved_name": partner_name,
            }
        )
        return request.redirect(f"/shop/booking/{index + 1}/schedule")
