# Copyright 2021 Tecnativa - Jairo Llopis
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import time
from datetime import datetime

from freezegun import freeze_time

from odoo import Command
from odoo.tests import HttpCase, new_test_user, tagged
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
from odoo.addons.website.tools import MockRequest

from ...resource_booking.tests.common import create_test_data
from ...website_sale_resource_booking.controllers.main import WebsiteSale


@tagged("post_install", "-at_install")
class UICase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        create_test_data(cls)
        cls.public_customer = cls.env["res.partner"].create({"name": "Customer X"})
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

    def setUp(self):
        super().setUp()
        self.ResourceBookingController = WebsiteSale()

    @freeze_time("2021-02-26 09:00:00", tick=True)
    def test_checkout(self):
        """Booking checkout tour."""
        # A visitor called Mr. A buys 3 booking products
        self.start_tour(
            "/shop", "website_sale_resource_booking", login="booking_test_user",
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
        so._onchange_partner_id_warning()
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
            [("state", "=", "outgoing"), ("subject", "not ilike", "Pending Order"),]
        )
        actual_invitations = {
            subject.strip()
            for subject in pending_mails.mapped("subject")
            if subject.startswith("Invitation to access")
        }
        expected_invitations = {
            "Invitation to access Mr. A - Test resource booking type - "
            "03/01/2021 at (09:00:00 To 09:30:00) (UTC)",
            "Invitation to access Mr. B - Test resource booking type - "
            "03/01/2021 at (09:00:00 To 09:30:00) (UTC)",
            "Invitation to access Mr. C - Test resource booking type - "
            "03/01/2021 at (09:30:00 To 10:00:00) (UTC)",
        }
        self.assertGreaterEqual(actual_invitations, expected_invitations)

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
            booking.start = dt
        self.assertEqual(bookings.mapped("state"), ["scheduled"] * 2)
        # Expiration cron does its job
        time.sleep(3)
        cron.method_direct_trigger()
        self.assertEqual(bookings.mapped("state"), ["canceled"] * 2)

    def test_booking_redirection_on_inactive_booking(self):
        website = self.env["website"].get_current_website()
        with MockRequest(self.env, website=website):
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
            bookings = order.resource_booking_ids
            bookings.action_cancel()
            self.ResourceBookingController._booking_redirection(bookings[0], 1)
            self.assertEqual(bookings.mapped("state"), ["pending"] * 2)
            self.ResourceBookingController._check_cart(order)

    def test_booking_sale_order(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_uom_qty": 2}
                    )
                ],
            }
        )
        order.write({"partner_id": self.public_customer.id})
        order._onchange_partner_id_warning()

    @mute_logger("odoo.models.unlink")
    def test_partner_id_change(self):
        """Abandoned cart expires bookings."""
        website = self.env["website"].create(
            {"name": "Test Website", "partner_id": self.partner.id}
        )
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
            booking.start = dt
        wizard = self.env["sale.order.booking.confirm"].create({"order_id": order.id,})
        self.assertEqual(order.resource_booking_count, 2)
        wizard = wizard.with_context(trigger_booking_email=True)
        wizard.action_invite()
        order._onchange_partner_id_warning()
        order.action_confirm()

    def test_variants_different_booking_timeout_and_expiration(self):
        """Test products with variants having different booking types and timeouts."""
        website = self.env["website"].get_current_website()
        rbt_1h = self.rbt.copy({"name": "Head Massage 1h", "duration": 1.0})
        rbt_2h = self.rbt.copy({"name": "Head Massage 2h", "duration": 2.0})

        attribute = self.env["product.attribute"].create({"name": "Duration"})
        val_1h = self.env["product.attribute.value"].create(
            {"name": "1 hour", "attribute_id": attribute.id}
        )
        val_2h = self.env["product.attribute.value"].create(
            {"name": "2 hours", "attribute_id": attribute.id}
        )

        template = self.env["product.template"].create(
            {
                "name": "Head massage",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, [val_1h.id, val_2h.id])],
                        },
                    )
                ],
            }
        )

        self.assertEqual(len(template.product_variant_ids), 2)
        v_1h = template.product_variant_ids.filtered(
            lambda p: val_1h
            in p.product_template_attribute_value_ids.product_attribute_value_id
        )
        v_2h = template.product_variant_ids.filtered(
            lambda p: val_2h
            in p.product_template_attribute_value_ids.product_attribute_value_id
        )

        v_1h.write(
            {"resource_booking_type_id": rbt_1h.id, "resource_booking_timeout": 1.0}
        )
        v_2h.write(
            {"resource_booking_type_id": rbt_2h.id, "resource_booking_timeout": 2.0}
        )

        self.assertEqual(v_1h.resource_booking_timeout, 1.0)
        self.assertEqual(v_2h.resource_booking_timeout, 2.0)
        self.assertTrue(v_1h.resource_booking_expiration)
        self.assertTrue(v_2h.resource_booking_expiration)
        diff_hours = (
            v_2h.resource_booking_expiration - v_1h.resource_booking_expiration
        ).total_seconds() / 3600
        self.assertAlmostEqual(diff_hours, 1.0, places=1)
        self.assertEqual(
            self.env["product.product"].search(
                [("resource_booking_timeout", "=", 2.0)]
            ),
            v_2h,
        )
        self.assertIn(
            template,
            self.env["product.template"].search(
                [("resource_booking_timeout", "=", 2.0)]
            ),
        )

        # Add variants to eCommerce cart
        order = (
            self.env["sale.order"]
            .with_context(website_id=website.id)
            .create(
                {
                    "website_id": website.id,
                    "partner_id": self.partner.id,
                    "order_line": [
                        Command.create({"product_id": v_1h.id, "product_uom_qty": 1}),
                        Command.create({"product_id": v_2h.id, "product_uom_qty": 1}),
                    ],
                }
            )
        )
        self.assertEqual(len(order.resource_booking_ids), 2)
        line_1h = order.order_line.filtered(lambda line: line.product_id == v_1h)
        line_2h = order.order_line.filtered(lambda line: line.product_id == v_2h)

        booking_1h = line_1h.resource_booking_ids
        booking_2h = line_2h.resource_booking_ids

        self.assertEqual(booking_1h.type_id, rbt_1h)
        self.assertEqual(booking_2h.type_id, rbt_2h)
        self.assertEqual(booking_1h.expiration, v_1h.resource_booking_expiration)
        self.assertEqual(booking_2h.expiration, v_2h.resource_booking_expiration)

    def test_product_without_variants_default_timeout(self):
        """Single variant product uses the timeout configured on template."""
        template = self.env["product.template"].create(
            {
                "name": "Single variant bookable product",
                "resource_booking_type_id": self.rbt.id,
                "resource_booking_timeout": 3.0,
            }
        )
        self.assertEqual(len(template.product_variant_ids), 1)
        variant = template.product_variant_ids[0]
        self.assertEqual(variant.resource_booking_timeout, 3.0)

        # Changing template timeout updates variant
        template.resource_booking_timeout = 4.5
        self.assertEqual(variant.resource_booking_timeout, 4.5)

    def test_multi_variant_timeout_isolation(self):
        """For products with multiple variants, configuring timeout on one variant does not affect other variants or the template."""
        attribute = self.env["product.attribute"].create({"name": "Option"})
        val_a = self.env["product.attribute.value"].create(
            {"name": "Option A", "attribute_id": attribute.id}
        )
        val_b = self.env["product.attribute.value"].create(
            {"name": "Option B", "attribute_id": attribute.id}
        )

        template = self.env["product.template"].create(
            {
                "name": "Template with multiple variants",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, [val_a.id, val_b.id])],
                        },
                    )
                ],
            }
        )
        self.assertEqual(len(template.product_variant_ids), 2)
        v_a = template.product_variant_ids.filtered(
            lambda p: val_a
            in p.product_template_attribute_value_ids.product_attribute_value_id
        )
        v_b = template.product_variant_ids.filtered(
            lambda p: val_b
            in p.product_template_attribute_value_ids.product_attribute_value_id
        )

        v_a.resource_booking_timeout = 5.0
        self.assertEqual(v_a.resource_booking_timeout, 5.0)
        self.assertEqual(v_b.resource_booking_timeout, 1.0)
        self.assertFalse(template.resource_booking_timeout)

    def test_booking_controller_flow(self):
        website = self.env["website"].get_current_website()
        order = (
            self.env["sale.order"]
            .with_context(website_id=website.id)
            .create(
                {
                    "website_id": website.id,
                    "partner_id": self.partner.id,
                    "order_line": [
                        Command.create(
                            {"product_id": self.product.id, "product_uom_qty": 1}
                        )
                    ],
                }
            )
        )
        booking = order.resource_booking_ids[0]
        booking.with_context(checkout_booking_index=1)._compute_access_url()
        self.assertEqual(booking.access_url, "/shop/booking/1")

        with MockRequest(self.env, website=website, sale_order_id=order.id):
            steps = website._get_checkout_step_list()
            self.assertTrue(
                any(
                    step[0] == "website_sale_resource_booking.scheduling"
                    for step in steps
                )
            )
            # Test schedule page rendering
            res = self.ResourceBookingController.booking_schedule(1)
            self.assertEqual(res.status_code, 200)
            # Test schedule beyond count redirects to checkout
            redirection = self.ResourceBookingController.booking_schedule(2)
            self.assertEqual(redirection.status_code, 303)
            self.assertEqual(redirection.location, "/shop/checkout")
            # Test confirm booking
            confirm_res = self.ResourceBookingController.booking_confirm(
                1,
                partner_name="Test Partner",
                partner_email="testpartner@example.com",
                when="2021-03-01T09:00:00Z",
            )
            self.assertEqual(confirm_res.status_code, 303)
            self.assertEqual(confirm_res.location, "/shop/booking/2/schedule")
            self.assertEqual(booking.prereserved_name, "Test Partner")
            self.assertEqual(booking.prereserved_email, "testpartner@example.com")
            # Confirming SO confirms prereservation
            order.action_confirm()
            self.assertEqual(booking.state, "confirmed")
            self.assertEqual(booking.partner_id.email, "testpartner@example.com")

    def test_template_and_product_without_booking_type(self):
        self.assertFalse(self.normal_product.resource_booking_expiration)
        self.assertFalse(
            self.normal_product.product_tmpl_id.resource_booking_expiration
        )
        self.assertTrue(self.product.resource_booking_expiration)
        self.assertTrue(self.product.product_tmpl_id.resource_booking_expiration)
