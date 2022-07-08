/* Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_require_legal.tour", function (require) {
    "use strict";

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
            run: "text 12345",
            trigger: ".checkout_autoformat input[name=zip]",
        },
        {
            run: "text Japan",
            trigger: ".checkout_autoformat select[name=country_id]",
        },
        {
            run: "text Yamagata",
            trigger: ".checkout_autoformat select[name=state_id]",
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
            trigger: "#checkbox_cgv",
        },
        {
            trigger: '#payment_method label:contains("Wire Transfer")',
        },
        {
            extra_trigger:
                '#payment_method label:contains("Wire Transfer") input:checked,#payment_method:not(:has("input:radio:visible"))',
            trigger: 'button[id="o_payment_form_pay"]:visible:not(:disabled)',
        },
        {
            // HACK https://github.com/odoo/odoo/blob/0a57e10accfa12dae5fea5bb8cb65b90bdf6e839/addons/website_sale/static/tests/tours/website_sale_buy.js#L76-L85
            trigger: '.oe_website_sale:contains("Please make a payment to:")',
        },
    ];

    tour.register(
        "website_sale_require_legal",
        {
            url: "/shop",
            test: true,
        },
        steps
    );

    return {
        steps: steps,
    };
});
