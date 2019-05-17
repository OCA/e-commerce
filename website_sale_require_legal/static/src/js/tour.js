/* Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_require_legal.tour", function (require) {
    "use strict";

    var base = require('web_editor.base');
    var tour = require("web_tour.tour");

    // Get an option value by its text
    // HACK https://github.com/odoo/odoo/pull/32718
    function opt_val (option_text) {
        return function (action_helper) {
            var option_id = this.$anchor.children(_.str.sprintf(
                "option:contains('%s')", option_text
            )).val();
            action_helper.text(option_id);
        };
    }

    var steps = [
        // Buy chair floor protection
        {
            trigger: '.oe_product_cart a:contains("Chair floor protection")',
        },
        {
            trigger: "#add_to_cart",
        },
        {
            trigger: ".btn:contains('Process Checkout')",
        },
        // Fill all required fields except legal terms acceptance
        {
            run: "text Super Mario",
            trigger: ".checkout_autoformat input[name=name]",
        },
        {
            run: "text mario@example.com",
            trigger: ".checkout_autoformat input[name=email]",
        },
        {
            run: "text 000 000 000",
            trigger: ".checkout_autoformat input[name=phone]",
        },
        {
            run: "text Castle St., 1",
            trigger: ".checkout_autoformat input[name=street]",
        },
        {
            run: "text Mushroom Kingdom",
            trigger: ".checkout_autoformat input[name=city]",
        },
        {
            run: opt_val("Japan"),
            trigger: ".checkout_autoformat select[name=country_id]",
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
