# Copyright 2021 Tecnativa - Jairo Llopis
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import time
from datetime import datetime

from freezegun import freeze_time

from odoo import Command
from odoo.tests.common import Form, HttpCase, new_test_user, tagged
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT

from ...resource_booking.tests.common import create_test_data


@tagged("post_install", "-at_install")
class UICase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        create_test_data(cls)
        cls.product = cls.env["product.product"].create(
            {
                "list_price": 100,
                "name": "test bookable product",
                "resource_booking_type_id": cls.rbt.id,
                "website_published": True,
            }
        )
        cls.normal_product = cls.env["product.product"].create(
            {
                "list_price": 50,
                "name": "test not bookable product",
                "website_published": True,
            }
        )
        # If the created user has the same name as the invited users,
        # the invitation does not reach the user.
        cls.user = new_test_user(cls.env, login="booking_test_user")
        # Clean up pending emails, to avoid polluting tests
        cls.env["mail.mail"].search([("state", "=", "outgoing")]).unlink()

    @freeze_time("2021-02-26 09:00:00", tick=True)
    def test_checkout(self):
        """Booking checkout tour."""
        # A visitor called Mr. A buys 3 booking products
        self.start_tour(
            "/shop",
            "website_sale_resource_booking",
            login="booking_test_user",
        )
        # Find Mr. A's cart
        so = self.env["sale.order"].search(
            [("partner_id", "=", self.user.partner_id.id)]
        )
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
        # The mail queue, later, will send the expected notifications to see
        # resource bookings in portal, but not to event attendance
        pending_mails = self.env["mail.mail"].search(
            [("state", "=", "outgoing"), ("subject", "not ilike", "Pending Order")]
        )
        self.assertGreaterEqual(
            set(pending_mails.mapped("subject")),
            {
                # Calendar invitations with attached .ics file
                "Invitation to Mr. A - Test resource booking type",
                "Invitation to Mr. B - Test resource booking type",
                "Invitation to Mr. C - Test resource booking type",
                # Portal invitations with tokenized link
                "Invitation to access Mr. A - Test resource booking type "
                "- 03/01/2021 at (09:00:00 To 09:30:00) (UTC)",
                "Invitation to access Mr. B - Test resource booking type "
                "- 03/01/2021 at (09:00:00 To 09:30:00) (UTC)",
                "Invitation to access Mr. C - Test resource booking type "
                "- 03/01/2021 at (09:30:00 To 10:00:00) (UTC)",
            },
        )

    @mute_logger("odoo.models.unlink")
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
                        Command.create(
                            {"product_id": self.product.id, "product_uom_qty": 2}
                        )
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
