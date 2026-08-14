/* Copyright 2021 Tecnativa - Jairo Llopis
   Copyright 2025 Tecnativa - Víctor Martínez
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import * as tourUtils from "@website_sale/js/tours/tour_utils";
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_resource_booking", {
    url: "/shop",
    steps: () => [
        // Add non-bookable product, to make sure we don't interfere
        ...tourUtils.addToCart({
            productName: "test not bookable product",
            expectUnloadPage: true,
        }),
        {
            trigger: "a[href='/shop']",
            run: "click",
            expectUnloadPage: true,
        },
        // Select bookable product
        ...tourUtils.searchProduct("test bookable product", {
            select: true,
            expectUnloadPage: true,
        }),
        // Make sure it displays the booking message
        {
            trigger:
                ".alert-info:contains('From the cart, you will be able to make a pre-reservation, which will expire in 1 hour')",
        },
        // Add one more
        {
            trigger: ".css_quantity_plus",
            run: "click",
        },
        // When there's 2 products, add another one
        {
            trigger: ".css_quantity .quantity",
            run({queryFirst}) {
                if (queryFirst(".css_quantity .quantity").value !== "2") {
                    throw new Error("Expected product quantity to be 2");
                }
            },
        },
        {
            trigger: ".css_quantity_plus",
            run: "click",
        },
        // When there's 3 products, add to cart
        {
            trigger: ".css_quantity .quantity",
            run({queryFirst}) {
                if (queryFirst(".css_quantity .quantity").value !== "3") {
                    throw new Error("Expected product quantity to be 3");
                }
            },
        },
        {
            trigger: "#add_to_cart",
            run: "click",
        },
        tourUtils.goToCart({quantity: 4}),
        // Go to next step
        {
            trigger: "a[name='website_sale_main_button']:contains('Schedule bookings')",
            run: "click",
            expectUnloadPage: true,
        },

        // Booking 1 of 3
        {
            trigger: "h3:contains('Pre-schedule your booking (1 of 3)')",
        },
        {
            trigger: ".o_booking_calendar:contains('February 2021')",
        },
        // No free slots on February, go to March as suggested
        {
            trigger:
                ".alert-danger:contains('No free slots found this month.') a:contains('Try next month')",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "h3:contains('Pre-schedule your booking (1 of 3)')",
        },
        {
            trigger: ".o_booking_calendar:contains('March 2021')",
        },
        // Open dropdown for March 1st
        {
            trigger: "#dropdown-trigger-2021-03-01",
            run: "click",
        },
        // Select 09:00
        {
            trigger:
                ".dropdown:has(#dropdown-trigger-2021-03-01) .dropdown-menu button:contains('09:00')",
            run: "click",
        },
        // Enter Mr. A details, and confirm
        {
            trigger: ".modal-dialog input[name=partner_name]",
            run: "edit Mr. A",
        },
        {
            trigger: ".modal-dialog input[name=partner_email]",
            run: "edit mr.a@example.com",
        },
        // Check we have an alert about payment timeout
        {
            trigger:
                ".alert-warning:contains('If unpaid, this pre-reservation will expire in 1 hour')",
        },
        {
            trigger: ".modal-dialog .btn:contains('Confirm booking')",
            run: "click",
            expectUnloadPage: true,
        },

        // Booking 2 of 3
        {
            trigger: "h3:contains('Pre-schedule your booking (2 of 3)')",
        },
        {
            trigger: ".o_booking_calendar:contains('February 2021')",
        },
        {
            trigger:
                ".alert-danger:contains('No free slots found this month.') a:contains('Try next month')",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "h3:contains('Pre-schedule your booking (2 of 3)')",
        },
        {
            trigger: ".o_booking_calendar:contains('March 2021')",
        },
        {
            trigger: "#dropdown-trigger-2021-03-01",
            run: "click",
        },
        {
            trigger:
                ".dropdown:has(#dropdown-trigger-2021-03-01) .dropdown-menu button:contains('09:00')",
            run: "click",
        },
        // Enter Mr. B details, and confirm
        {
            trigger: ".modal-dialog input[name=partner_name]",
            run: "edit Mr. B",
        },
        {
            trigger: ".modal-dialog input[name=partner_email]",
            run: "edit mr.b@example.com",
        },
        {
            trigger:
                ".alert-warning:contains('If unpaid, this pre-reservation will expire in 1 hour')",
        },
        {
            trigger: ".modal-dialog .btn:contains('Confirm booking')",
            run: "click",
            expectUnloadPage: true,
        },

        // Booking 3 of 3
        {
            trigger: "h3:contains('Pre-schedule your booking (3 of 3)')",
        },
        {
            trigger: ".o_booking_calendar:contains('February 2021')",
        },
        {
            trigger:
                ".alert-danger:contains('No free slots found this month.') a:contains('Try next month')",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "h3:contains('Pre-schedule your booking (3 of 3)')",
        },
        {
            trigger: ".o_booking_calendar:contains('March 2021')",
        },
        {
            trigger:
                "tfoot:contains('All times are displayed using this timezone: UTC')",
        },
        {
            trigger: "#dropdown-trigger-2021-03-01",
            run: "click",
        },
        // This time 09:00 is full because RBT has only 2 RBC available
        {
            trigger:
                ".dropdown:has(#dropdown-trigger-2021-03-01) .dropdown-menu:not(:has(button:contains('09:00')))",
        },
        {
            trigger:
                ".dropdown:has(#dropdown-trigger-2021-03-01) .dropdown-menu button:contains('09:30')",
            run: "click",
        },

        // Enter Mr. C details, and confirm
        {
            trigger: ".modal-dialog input[name=partner_name]",
            run: "edit Mr. C",
        },
        {
            trigger: ".modal-dialog input[name=partner_email]",
            run: "edit mr.c@example.com",
        },
        {
            trigger:
                ".alert-warning:contains('If unpaid, this pre-reservation will expire in 1 hour')",
        },
        {
            trigger: ".modal-dialog .btn:contains('Confirm booking')",
            run: "click",
            expectUnloadPage: true,
        },

        // Fill buyer address
        {
            trigger: "#o_country_id",
            run: "selectByLabel Belgium",
        },
        {
            trigger: 'form.address_autoformat input[name="phone"]',
            run: "edit +32 485 118.218",
        },
        {
            trigger: 'form.address_autoformat input[name="street"]',
            run: "edit Street A",
        },
        {
            trigger: 'form.address_autoformat input[name="city"]',
            run: "edit City A",
        },
        {
            trigger: 'form.address_autoformat input[name="zip"]',
            run: "edit 18503",
        },
        // Integration with website_sale_vat_required
        {
            trigger: 'form.address_autoformat input[name="vat"]',
            run: "edit US01234567891",
        },
        {
            trigger: "a[name='website_sale_main_button']",
            run: "click",
            expectUnloadPage: true,
        },
    ],
});
