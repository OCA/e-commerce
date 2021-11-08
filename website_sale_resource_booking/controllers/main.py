# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime
from urllib.parse import quote_plus

from dateutil.parser import isoparse

from odoo import _
from odoo.exceptions import ValidationError
from odoo.http import request, route
from odoo.tests.common import Form

from ...website_sale.controllers import main


class WebsiteSale(main.WebsiteSale):
    def _get_bookings(self):
        """Obtain bookings from current cart."""
        order = request.website.sale_get_order()
        return order.mapped("order_line.resource_booking_ids")

    def _get_indexed_booking(self, index):
        """Get indexed booking from current cart.

        :param int index: 1 is the 1st element.
        """
        bookings = self._get_bookings().sorted("id")
        if index > len(bookings):
            raise IndexError()
        return bookings[index - 1]

    def checkout_redirection(self, order):
        """Redirect to scheduling bookings if still not done."""
        order.order_line._sync_resource_bookings()
        bookings = order.mapped("order_line.resource_booking_ids")
        for booking in bookings:
            if booking.state == "pending":
                return request.redirect("/shop/booking/1/schedule")
        return super().checkout_redirection(order)

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
        count = len(bookings)
        values = booking._get_calendar_context(year, month)
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
        when_tz_aware = isoparse(when)
        when_naive = datetime.utcfromtimestamp(when_tz_aware.timestamp())
        try:
            with Form(booking_sudo) as booking_form:
                booking_form.start = when_naive
        except ValidationError as error:
            url = "/shop/booking/{}/schedule?error={}".format(
                index, quote_plus(error.name)
            )
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
        return request.redirect("/shop/booking/{}/schedule".format(index + 1))
