/* Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_require_legal.tour", function(require) {
    "use strict";

    var base = require("web_editor.base");
    var tour = require("web_tour.tour");

    var steps = [
        {
            trigger: '.oe_product_cart a:contains("Customizable")',
        },
        {
            trigger: "#add_to_cart",
        },
        {
            trigger: ".btn:contains('Process Checkout')",
        },
        // Fill all required fields except legal terms acceptance
        {
            run: "text mario@example.com",
            trigger: ".checkout_autoformat input[name=email]",
        },
        // Submit, to check the lack of acceptance is a failure
        {
            trigger: ".btn-primary:contains('Next')",
        },
        // Accept legal terms and accept again
        {
            trigger: "#accepted_legal_terms.is-invalid",
        },
        {
            trigger: ".btn-primary:contains('Next')",
        },
        {
            trigger: ".btn-primary:contains('Confirm')",
        },
        // If I can proceed to payment, it's because the form validated fine
        {
            trigger: ".btn-primary:contains('Pay Now')",
        },
    ];

    tour.register(
        "website_sale_require_legal",
        {
            url: "/shop",
            test: true,
            wait_for: base.ready(),
        },
        steps
    );

    return {
        steps: steps,
    };
});
