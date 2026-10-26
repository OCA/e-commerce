/** @odoo-module */
/* Copyright 2021 Tecnativa - Jairo Llopis
   Copyright 2025 Tecnativa - Víctor Martínez
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
import * as tourUtils from "@website_sale/js/tours/tour_utils";

registry.category("web_tour.tours").add("website_sale_resource_booking", {
    url: "/shop",
    steps: () => [
        ...tourUtils.searchProduct("test not bookable product"),
        {
            content: "select test not bookable product",
            trigger: '.oe_product_cart:first a:contains("test not bookable product")',
            run: "click",
        },
        {
            content: "click on add to cart",
            trigger: '#product_detail form[action^="/shop/cart/update"] #add_to_cart',
            run: "click",
        },
        ...tourUtils.searchProduct("test bookable product"),
        {
            trigger: 'form input[name="search"]',
            run: "edit test bookable product",
        },
        {
            trigger: 'form:has(input[name="search"]) .oe_search_button',
        },
        {
            content: "select test bookable product",
            trigger: '.oe_product_cart:first a:contains("test bookable product")',
            run: "click",
        },
        {
            content: "change quantity",
            trigger:
                '#product_detail form[action^="/shop/cart/update"] input[name=add_qty]',
            run: "edit 3",
        },
        {
            content: "click on add to cart",
            trigger: '#product_detail form[action^="/shop/cart/update"] #add_to_cart',
            run: "click",
        },

        tourUtils.goToCart({quantity: 4}),
        {
            // Go to next step
            trigger: "a[name='website_sale_main_button']:contains('Schedule bookings')",
            run: "click",
        },
        {
            content: "Calendar is loaded",
            trigger: ".o_booking_calendar",
        },
        {
            content: "Validate calendar title is shown",
            trigger: "h3:contains('Pre-schedule your booking')",
        },
        {
            content: "Try next month if no slots",
            trigger: ".alert-danger a:contains('Try next month')",
            run: "click",
        },
        {
            content: "Open March 1 calendar dropdown",
            trigger: "#dropdown-trigger-2021-03-01",
            run: "click",
        },
        {
            trigger:
                ".dropdown:has(#dropdown-trigger-2021-03-01) .dropdown-menu button:contains('09:00')",
            run: "click",
        },
        {
            trigger:
                '.modal.show input[name="partner_name"], .modal input[name="partner_name"]',
            run: "edit Mr. A",
        },
        {
            trigger:
                '.modal.show input[name="partner_email"], .modal input[name="partner_email"], .modal input[name="email"]',
            run: "edit mr.a@example.com",
        },
        {
            trigger: ".modal-dialog .btn:contains('Confirm booking')",
            run: "click",
        },
        // Booking 2 of 3 (almost same as above)
        {
            content: "Try next month if no slots",
            trigger: ".alert-danger a:contains('Try next month')",
            run: "click",
        },
        {
            content: "Open March 1 calendar dropdown",
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
            trigger:
                '.modal.show input[name="partner_name"], .modal input[name="partner_name"]',
            run: "edit Mr. B",
        },
        {
            trigger:
                '.modal.show input[name="partner_email"], .modal input[name="partner_email"], .modal input[name="email"]',
            run: "edit mr.b@example.com",
        },
        {
            trigger: ".modal-dialog .btn:contains('Confirm booking')",
            run: "click",
        },
        {
            content: "Try next month if no slots",
            trigger: ".alert-danger a:contains('Try next month')",
            run: "click",
        },
        {
            content: "Open March 1 calendar dropdown",
            trigger: "#dropdown-trigger-2021-03-01",
            run: "click",
        },

        {
            trigger:
                ".dropdown:has(#dropdown-trigger-2021-03-01) .dropdown-menu button:contains('09:30')",
            run: "click",
        },
        // Enter Mr. B details, and confirm
        {
            trigger:
                '.modal.show input[name="partner_name"], .modal input[name="partner_name"]',
            run: "edit Mr. C",
        },
        {
            trigger:
                '.modal.show input[name="partner_email"], .modal input[name="partner_email"], .modal input[name="email"]',
            run: "edit mr.c@example.com",
        },
        {
            trigger: ".modal-dialog .btn:contains('Confirm booking')",
            run: "click",
        },
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
        tourUtils.goToCheckout(),
    ],
});
