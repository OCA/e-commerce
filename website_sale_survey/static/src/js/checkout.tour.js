/* Copyright 2021 Tecnativa - Jairo Llopis
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_survey.tour_checkout", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    tour.register(
        "website_sale_survey_checkout",
        {
            test: true,
            url: "/shop",
            wait_for: base.ready(),
        },
        [
            // Add normal product to cart
            {trigger: ".oe_search_box", run: "text website_sale_survey"},
            {trigger: ".oe_search_button"},
            {
                trigger: ".oe_product_cart a:contains('product without surveys')",
            },
            {trigger: "#add_to_cart"},
            {trigger: ".btn:contains('Continue Shopping')"},
            // Add survey product 1
            {trigger: ".oe_search_box", run: "text website_sale_survey"},
            {trigger: ".oe_search_button"},
            {
                trigger: ".oe_product_cart a:contains('product with surveys 1')",
            },
            {trigger: "#add_to_cart"},
            {
                extra_trigger: [
                    ".js_cart_lines",
                    // There's an alert telling you about pending surveys
                    ":has(.alert-warning.js_pending_survey)",
                    // Product 1 has a pending surveys badge
                    ":has(.td-product_name:contains('product with surveys 1') .badge-warning.js_pending_survey)",
                ].join(""),
                trigger: ".btn:contains('Continue Shopping')",
            },
            // Add survey product 2
            {trigger: ".oe_search_box", run: "text website_sale_survey"},
            {trigger: ".oe_search_button"},
            {
                trigger: ".oe_product_cart a:contains('product with surveys 2')",
            },
            {trigger: "#add_to_cart"},
            {
                extra_trigger: [
                    ".js_cart_lines",
                    // Products 1 and 2 have pending surveys badges
                    ":has(.td-product_name:contains('product with surveys 1') .badge-warning.js_pending_survey)",
                    ":has(.td-product_name:contains('product with surveys 2') .badge-warning.js_pending_survey)",
                ].join(""),
                // Buyer clicks on "Fill survey" in the alert
                trigger: ".alert-warning.js_pending_survey .alert-link",
            },
            // Fill survey for product 1
            {trigger: ".btn:contains('Start Survey')"},
            {
                trigger: ".js_question-wrapper:contains('are you a robot?') input",
                run: "text of course",
            },
            {trigger: ".btn:contains('Submit survey')"},
            {trigger: ".btn:contains('Return to cart')"},
            {
                extra_trigger: [
                    ".js_cart_lines",
                    // There's an alert telling you about pending surveys
                    ":has(.alert-warning.js_pending_survey)",
                    // Product 1 survey is done
                    ":has(.td-product_name:contains('product with surveys 1') .badge-success.js_pending_survey)",
                    // Product 2 survey is pending
                    ":has(.td-product_name:contains('product with surveys 2') .badge-warning.js_pending_survey)",
                ].join(""),
                // Buyer clicks on "Process Checkout"; didn't realize about the other survey
                trigger: ".btn:contains('Process Checkout')",
            },
            // Fill survey for product 2
            {trigger: ".btn:contains('Start Survey')"},
            {
                trigger: ".js_question-wrapper:contains('are you a robot?') input",
                run: "text again?",
            },
            {trigger: ".btn:contains('Submit survey')"},
            {trigger: ".btn:contains('Return to cart')"},
            {
                extra_trigger: [
                    ".js_cart_lines",
                    // No more pending surveys alerts
                    ":not(:has(.alert.js_pending_survey))",
                    // Product 2 survey is done
                    ":has(.td-product_name:contains('product with surveys 2') .badge-success.js_pending_survey)",
                ].join(""),
                // Buyer wants to review Product 1 survey
                trigger:
                    ".td-product_name:contains('product with surveys 1') .badge-success.js_pending_survey",
            },
            {
                // The answer I gave is still OK
                extra_trigger: ".js_question-wrapper input:propValue('of course')",
                // Return to cart
                trigger: "#my_cart .badge:contains(3)",
            },
            {
                trigger: ".btn:contains('Process Checkout')",
            },
            // We got to the "Address" step, so it should be OK from here
            {
                trigger: "input[name=name]",
                run: "text I have a name",
            },
        ]
    );
});
