# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import time
from datetime import datetime

from freezegun import freeze_time

from odoo.tests.common import Form, HttpCase

from ...resource_booking.tests.common import create_test_data


@freeze_time("2021-02-26 09:00:00", tick=True)
class UICase(HttpCase):
    def setUp(self):
        super().setUp()
        create_test_data(self)
        self.product = self.env["product.product"].create(
            {
                "list_price": 100,
                "name": "test bookable product",
                "resource_booking_type_id": self.rbt.id,
                "website_published": True,
            }
        )
        self.normal_product = self.env["product.product"].create(
            {
                "list_price": 50,
                "name": "test not bookable product",
                "website_published": True,
            }
        )
        # Clean up pending emails, to avoid polluting tests
        self.env["mail.mail"].search([("state", "=", "outgoing")]).unlink()

    def test_checkout(self):
        """Booking checkout tour."""
        # A visitor called Mr. A buys 3 booking products
        self.start_tour(
            "/shop?search=test not bookable product",
            "website_sale_resource_booking_checkout",
        )
        # Find Mr. A's cart
        so = self.env["sale.order"].search([("partner_id", "=", "Mr. A")])
        bookings = so.resource_booking_ids
        # It's linked to 3 scheduled bookings, that belong to him
        self.assertEqual(len(bookings), 3)
        self.assertEqual(bookings.mapped("state"), ["scheduled"] * 3)
        self.assertEqual(bookings.mapped("partner_id"), so.partner_id)
        # Confirm sale (which would happen automatically if paid online)
        so.action_confirm()
        # Now the 3 bookings are linked to the partners filled at checkout
        self.assertEqual(
            set(bookings.mapped("partner_id.name")), {"Mr. A", "Mr. B", "Mr. C"}
        )
        self.assertEqual(
            set(bookings.mapped("partner_id.email")),
            {"mr.a@example.com", "mr.b@example.com", "mr.c@example.com"},
        )
        # One of those partners is the same that bought
        self.assertIn(so.partner_id, bookings.mapped("partner_id"))
        # The mail queue, later, will send the expected notifications to see
        # resource bookings in portal, but not to event attendance
        pending_mails = self.env["mail.mail"].search([("state", "=", "outgoing")])
        self.assertLessEqual(
            set(pending_mails.mapped("subject")),
            {
                # Calendar invitations with attached .ics file
                "Invitation to Mr. A - Test resource booking type",
                "Invitation to Mr. B - Test resource booking type",
                "Invitation to Mr. C - Test resource booking type",
                # Portal invitations with tokenized link
                "You are invited to access Mr. A - Test resource booking type "
                "- 03/01/2021 at (09:00:00 To 09:30:00) (UTC)",
                "You are invited to access Mr. B - Test resource booking type "
                "- 03/01/2021 at (09:00:00 To 09:30:00) (UTC)",
                "You are invited to access Mr. C - Test resource booking type "
                "- 03/01/2021 at (09:30:00 To 10:00:00) (UTC)",
            },
        )

    def test_expiration_cron(self):
        """Abandoned cart expires bookings."""
        website = self.env["website"].get_current_website()
        cron = self.browse_ref("website_sale_resource_booking.cron_expire")
        # Set product expiration to 2 second (approx... you know... floats)
        self.product.resource_booking_timeout = 2 / 60 / 60
        # Emulate a cart
        order = (
            self.env["sale.order"]
            .with_context(website_id=website.id)
            .create(
                {
                    "website_id": website.id,
                    "partner_id": self.partner.id,
                    "order_line": [
                        (0, 0, {"product_id": self.product.id, "product_uom_qty": 2})
                    ],
                }
            )
        )
        self.assertEqual(len(order.resource_booking_ids), 2)
        # Emulate the user prereserved both bookings
        dt = datetime(2021, 3, 1, 9)
        bookings = order.resource_booking_ids
        for booking in bookings:
            with Form(booking) as booking_f:
                booking_f.start = dt
        self.assertEqual(bookings.mapped("state"), ["scheduled"] * 2)
        # Expiration cron does its job
        time.sleep(3)
        cron.method_direct_trigger()
        self.assertEqual(bookings.mapped("state"), ["canceled"] * 2)
