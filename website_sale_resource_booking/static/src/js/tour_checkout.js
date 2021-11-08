/* Copyright 2021 Tecnativa - Jairo Llopis
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_resource_booking.tour_checkout", function(require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "website_sale_resource_booking_checkout",
        {
            url: "/shop?search=test not bookable product",
            test: true,
        },
        [
            // Add non-bookable product, to make sure we don't interfere
            {
                trigger: ".oe_product_cart a:contains('test not bookable product')",
            },
            {
                trigger: "#add_to_cart",
            },
            {
                trigger: ".btn:contains('Continue Shopping')",
            },
            {
                trigger: ".oe_search_box",
                run: "text test bookable product",
            },
            {
                trigger: ".oe_search_button",
            },
            // Select bookable product
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
            {
                // Check there's a booking step advertised in the checkout wizard
                extra_trigger:
                    ".progress-wizard-step.disabled:contains('Schedule bookings')",
                // Go to next step
                trigger: ".oe_cart .btn:contains('Process Checkout')",
            },
            // Booking 1 of 3
            {
                extra_trigger: [
                    ".oe_website_sale",
                    // Check we're in the correct booking step
                    ":has(.progress-wizard-step.active:contains('Schedule bookings'))",
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
                    ":has(.progress-wizard-step.active:contains('Schedule bookings'))",
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
                    ":has(.progress-wizard-step.active:contains('Schedule bookings'))",
                    ":has(h3:contains('Pre-schedule your booking (2 of 3)'))",
                    ":has(.o_booking_calendar:contains('February 2021'))",
                ].join(""),
                trigger:
                    ".alert-danger:contains('No free slots found this month.') a:contains('Try next month')",
            },
            {
                extra_trigger: [
                    ".oe_website_sale",
                    ":has(.progress-wizard-step.active:contains('Schedule bookings'))",
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
                    ":has(.progress-wizard-step.active:contains('Schedule bookings'))",
                    ":has(h3:contains('Pre-schedule your booking (3 of 3)'))",
                    ":has(.o_booking_calendar:contains('February 2021'))",
                ].join(""),
                trigger:
                    ".alert-danger:contains('No free slots found this month.') a:contains('Try next month')",
            },
            {
                extra_trigger: [
                    ".oe_website_sale",
                    ":has(.progress-wizard-step.active:contains('Schedule bookings'))",
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
            {
                extra_trigger: [
                    ".oe_website_sale",
                    ":has(.progress-wizard-step.complete:contains('Schedule bookings'))",
                    ":has(.progress-wizard-step.active:contains('Address'))",
                ].join(""),
                trigger: ".oe_website_sale input[name=name]",
                run: "text Mr. A",
            },
            {
                trigger: ".oe_website_sale input[name=email]",
                run: "text mr.a@example.com",
            },
            {
                trigger: ".oe_website_sale input[name=phone]",
                run: "text +32 485 118.218",
            },
            {
                trigger: ".oe_website_sale input[name=street]",
                run: "text Street A",
            },
            {
                trigger: ".oe_website_sale input[name=city]",
                run: "text City A",
            },
            {
                trigger: ".oe_website_sale select[name=country_id]",
                run: "text Fiji",
            },
            {
                trigger: ".oe_website_sale",
                run: function() {
                    // Integration with website_sale_vat_required
                    $(".oe_website_sale input[name=vat]").val("US01234567891");
                    // Integration with website_sale_require_legal
                    $(".oe_website_sale input[name=accepted_legal_terms]").prop(
                        "checked",
                        true
                    );
                },
            },
            {
                trigger: ".oe_website_sale .btn:contains('Next')",
            },
            {
                trigger: '#payment_method label:contains("Wire Transfer")',
            },
            // No need to wait for payment for this test case; that's tested elsewhere
            {
                extra_trigger:
                    '#payment_method label:contains("Wire Transfer") input:checked,#payment_method:not(:has("input:radio:visible"))',
                trigger: 'button[id="o_payment_form_pay"]:visible:not(:disabled)',
            },
        ]
    );
});
