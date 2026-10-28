/* @odoo-module */
/* Copyright 2021 Tecnativa - Jairo Llopis
   Copyright 2025 Tecnativa - Víctor Martínez
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import * as tourUtils from "@website_sale/js/tours/tour_utils";
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_resource_booking", {
    url: "/shop",
    steps: () => [
        // Add non-bookable product, to make sure we don't interfere
        ...tourUtils.addToCart({productName: "test not bookable product"}),
        {
            content: "Wait until non-bookable product is added to cart",
            trigger: "a sup.my_cart_quantity:text(1)",
        },
        // Select bookable product
        ...tourUtils.searchProduct("test bookable product", {select: true}),
        {
            content: "Make sure it displays the booking message",
            trigger:
                ".alert-info:contains('From the cart, you will be able to make a pre-reservation, which will expire')",
        },
        {
            content: "Set quantity to 3",
            trigger:
                '#product_detail form[action^="/shop/cart/update"] input[name="add_qty"]',
            run: "edit 3",
        },
        {
            content: "Click add to cart",
            trigger: '#product_detail form[action^="/shop/cart/update"] #add_to_cart',
            run: "click",
        },
        tourUtils.goToCart({quantity: 4}),
        {
            content: "Go to booking scheduling step",
            trigger: "a[name='website_sale_main_button']:contains('Schedule bookings')",
            run: "click",
        },
        // Booking 1 of 3
        {
            content: "No free slots on February, go to March as suggested",
            trigger:
                ".oe_website_sale:has(h3:contains('Pre-schedule your booking (1 of 3)')) .alert-danger:contains('No free slots found this month.') a:contains('Try next month')",
            run: "click",
        },
        {
            content: "Open dropdown for March 1st (Booking 1)",
            trigger:
                ".oe_website_sale:has(h3:contains('Pre-schedule your booking (1 of 3)')) #dropdown-trigger-2021-03-01",
            run: "click",
        },
        {
            content: "Select 09:00 (Booking 1)",
            trigger:
                ".dropdown:has(#dropdown-trigger-2021-03-01) .dropdown-menu button:contains('09:00')",
            run: "click",
        },
        {
            content: "Enter Mr. A name",
            trigger: ".modal-dialog input[name='partner_name']",
            run: "edit Mr. A",
        },
        {
            content: "Enter Mr. A email",
            trigger: ".modal-dialog input[name='partner_email']",
            run: "edit mr.a@example.com",
        },
        {
            content: "Confirm Mr. A booking",
            trigger:
                ".modal-dialog:has(.alert-warning:contains('If unpaid, this pre-reservation will expire')) .btn:contains('Confirm booking')",
            run: "click",
        },
        // Booking 2 of 3
        {
            content: "No free slots on February, go to March as suggested (Booking 2)",
            trigger:
                ".oe_website_sale:has(h3:contains('Pre-schedule your booking (2 of 3)')) .alert-danger:contains('No free slots found this month.') a:contains('Try next month')",
            run: "click",
        },
        {
            content: "Open dropdown for March 1st (Booking 2)",
            trigger:
                ".oe_website_sale:has(h3:contains('Pre-schedule your booking (2 of 3)')) #dropdown-trigger-2021-03-01",
            run: "click",
        },
        {
            content: "Select 09:00 (Booking 2)",
            trigger:
                ".dropdown:has(#dropdown-trigger-2021-03-01) .dropdown-menu button:contains('09:00')",
            run: "click",
        },
        {
            content: "Enter Mr. B name",
            trigger: ".modal-dialog input[name='partner_name']",
            run: "edit Mr. B",
        },
        {
            content: "Enter Mr. B email",
            trigger: ".modal-dialog input[name='partner_email']",
            run: "edit mr.b@example.com",
        },
        {
            content: "Confirm Mr. B booking",
            trigger:
                ".modal-dialog:has(.alert-warning:contains('If unpaid, this pre-reservation will expire')) .btn:contains('Confirm booking')",
            run: "click",
        },
        // Booking 3 of 3
        {
            content: "No free slots on February, go to March as suggested (Booking 3)",
            trigger:
                ".oe_website_sale:has(h3:contains('Pre-schedule your booking (3 of 3)')) .alert-danger:contains('No free slots found this month.') a:contains('Try next month')",
            run: "click",
        },
        {
            content: "Open dropdown for March 1st (Booking 3)",
            trigger:
                ".oe_website_sale:has(h3:contains('Pre-schedule your booking (3 of 3)')) #dropdown-trigger-2021-03-01",
            run: "click",
        },
        {
            content: "Select 09:30 (Booking 3 - 09:00 is full)",
            trigger:
                ".dropdown:has(#dropdown-trigger-2021-03-01) .dropdown-menu button:contains('09:30')",
            run: "click",
        },
        {
            content: "Enter Mr. C name",
            trigger: ".modal-dialog input[name='partner_name']",
            run: "edit Mr. C",
        },
        {
            content: "Enter Mr. C email",
            trigger: ".modal-dialog input[name='partner_email']",
            run: "edit mr.c@example.com",
        },
        {
            content: "Confirm Mr. C booking",
            trigger:
                ".modal-dialog:has(.alert-warning:contains('If unpaid, this pre-reservation will expire')) .btn:contains('Confirm booking')",
            run: "click",
        },
        tourUtils.confirmOrder(),
    ],
});
