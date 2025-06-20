/** @odoo-module */
/* Copyright 2021 Tecnativa - Jairo Llopis
   Copyright 2025 Tecnativa - Víctor Martínez
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
import tourUtils from "@website_sale/js/tours/tour_utils";

registry.category("web_tour.tours").add("website_sale_resource_booking", {
    test: true,
    url: "/shop",
    steps: () => [
        // Add non-bookable product, to make sure we don't interfere
        ...tourUtils.addToCart({productName: "test not bookable product"}),
        // Select bookable product
        {
            trigger: ".oe_search_box",
            run: "text test bookable product",
        },
        {
            trigger: ".oe_search_button",
        },
        {
            trigger: ".oe_product_cart a:contains('test bookable product')",
        },
        {
            // Make sure it displays the booking message
            extra_trigger:
                ".alert-info:containsTextLike('From the cart, you will be able to make a pre-reservation, which will expire in 1 hour')",
            // Add one more
            trigger: ".css_quantity .fa-plus",
        },
        // When there's 2 products, add another one
        {
            extra_trigger: ".css_quantity .quantity:propValue('2')",
            trigger: ".css_quantity .fa-plus",
        },
        // When there's 3 products, add to cart
        {
            extra_trigger: ".css_quantity .quantity:propValue('3')",
            trigger: "#add_to_cart",
        },
        tourUtils.goToCart({quantity: 4}),
        {
            // Go to next step
            trigger: "a[name='website_sale_main_button']:contains('Schedule bookings')",
        },
        // Booking 1 of 3
        {
            extra_trigger: [
                ".oe_website_sale",
                // Check we're in the correct booking step
                ":has(.o_wizard_step_active:contains('Schedule bookings'))",
                ":has(h3:contains('Pre-schedule your booking (1 of 3)'))",
                // We're using freezegun, so date is hardcoded
                ":has(.o_booking_calendar:contains('February 2021'))",
            ].join(""),
            // No free slots on February, go to March as suggested
            trigger:
                ".alert-danger:contains('No free slots found this month.') a:contains('Try next month')",
        },
        {
            extra_trigger: [
                ".oe_website_sale",
                // Check we're in the correct booking step
                ":has(.o_wizard_step_active:contains('Schedule bookings'))",
                ":has(h3:contains('Pre-schedule your booking (1 of 3)'))",
                ":has(.o_booking_calendar:contains('March 2021'))",
            ].join(""),
            // Open dropdown for March 1st
            trigger: "#dropdown-trigger-2021-03-01",
        },
        // Select 09:00
        {
            trigger:
                ".dropdown:has(#dropdown-trigger-2021-03-01) .dropdown-menu button:contains('09:00')",
        },
        // Enter Mr. A details, and confirm
        {
            trigger: ".modal-dialog input[name=partner_name]",
            run: "text Mr. A",
        },
        {
            trigger: ".modal-dialog input[name=partner_email]",
            run: "text mr.a@example.com",
        },
        {
            // Check we have an alert about payment timeout
            extra_trigger:
                ".alert-warning:containsTextLike('If unpaid, this pre-reservation will expire in 1 hour')",
            trigger: ".modal-dialog .btn:contains('Confirm booking')",
        },
        // Booking 2 of 3 (almost same as above)
        {
            extra_trigger: [
                ".oe_website_sale",
                ":has(.o_wizard_step_active:contains('Schedule bookings'))",
                ":has(h3:contains('Pre-schedule your booking (2 of 3)'))",
                ":has(.o_booking_calendar:contains('February 2021'))",
            ].join(""),
            trigger:
                ".alert-danger:contains('No free slots found this month.') a:contains('Try next month')",
        },
        {
            extra_trigger: [
                ".oe_website_sale",
                ":has(.o_wizard_step_active:contains('Schedule bookings'))",
                ":has(h3:contains('Pre-schedule your booking (2 of 3)'))",
                ":has(.o_booking_calendar:contains('March 2021'))",
            ].join(""),
            trigger: "#dropdown-trigger-2021-03-01",
        },
        {
            trigger:
                ".dropdown:has(#dropdown-trigger-2021-03-01) .dropdown-menu button:contains('09:00')",
        },
        // Enter Mr. B details, and confirm
        {
            trigger: ".modal-dialog input[name=partner_name]",
            run: "text Mr. B",
        },
        {
            trigger: ".modal-dialog input[name=partner_email]",
            run: "text mr.b@example.com",
        },
        {
            extra_trigger:
                ".alert-warning:containsTextLike('If unpaid, this pre-reservation will expire in 1 hour')",
            trigger: ".modal-dialog .btn:contains('Confirm booking')",
        },
        // Booking 3 of 3
        {
            extra_trigger: [
                ".oe_website_sale",
                ":has(.o_wizard_step_active:contains('Schedule bookings'))",
                ":has(h3:contains('Pre-schedule your booking (3 of 3)'))",
                ":has(.o_booking_calendar:contains('February 2021'))",
            ].join(""),
            trigger:
                ".alert-danger:contains('No free slots found this month.') a:contains('Try next month')",
        },
        {
            extra_trigger: [
                ".oe_website_sale",
                ":has(.o_wizard_step_active:contains('Schedule bookings'))",
                ":has(h3:contains('Pre-schedule your booking (3 of 3)'))",
                ":has(.o_booking_calendar:contains('March 2021'))",
                ":has(tfoot:containsTextLike('All times are displayed using this timezone: UTC'))",
            ].join(""),
            trigger: "#dropdown-trigger-2021-03-01",
        },
        {
            // This time 09:00 is full because RBT has only 2 RBC available, and thus we can't see it
            extra_trigger:
                ".dropdown:has(#dropdown-trigger-2021-03-01) .dropdown-menu:not(:has(button:contains('09:00')))",
            trigger:
                ".dropdown:has(#dropdown-trigger-2021-03-01) .dropdown-menu button:contains('09:30')",
        },
        // Enter Mr. C details, and confirm
        {
            trigger: ".modal-dialog input[name=partner_name]",
            run: "text Mr. C",
        },
        {
            trigger: ".modal-dialog input[name=partner_email]",
            run: "text mr.c@example.com",
        },
        {
            extra_trigger:
                ".alert-warning:containsTextLike('If unpaid, this pre-reservation will expire in 1 hour')",
            trigger: ".modal-dialog .btn:contains('Confirm booking')",
        },
        // Fill buyer address
        tourUtils.goToCheckout(),
        {
            trigger: ".oe_website_sale",
            run: function () {
                $('input[name="phone"]').val("+32 485 118.218");
                $('input[name="street"]').val("Street A");
                $('input[name="city"]').val("City A");
                $('input[name="zip"]').val("18503");
                $("#country_id option:eq(1)").attr("selected", true);
                // Integration with website_sale_vat_required
                $('input[name="vat"]').val("US01234567891");
                // Integration with website_sale_require_legal
                $(".oe_website_sale input[name=accepted_legal_terms]").prop(
                    "checked",
                    true
                );
            },
        },
        {
            trigger: ".btn-primary:contains('Save address')",
        },
        {
            trigger: "a[href='/shop/confirm_order']",
        },
    ],
});
