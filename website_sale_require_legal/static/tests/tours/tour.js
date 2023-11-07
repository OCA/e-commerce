/* Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
 * Copyright 2023 Pilar Vargas <pilar.vargas@tecnativa.com>
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
            trigger: "button:contains('Proceed to Checkout')",
        },
        {
            trigger: "a[href='/shop/cart']",
            extra_trigger: "sup.my_cart_quantity:contains('1')",
        },
        {
            trigger: 'a:contains("Process Checkout")',
        },
        {
            trigger: "a[href='/shop/checkout']",
        },
        // Fill all required fields except legal terms acceptance
        {
            trigger: 'select[name="country_id"]',
            run: function () {
                $('input[name="phone"]').val("99999999");
                // Required for test compatibility with the website_sale_vat_required module
                $('input[name="vat"]').val("00000000X");
                $('input[name="street"]').val("Castle St., 1");
                $('input[name="city"]').val("Mushroom Kingdom");
                $('input[name="zip"]').val("10000");
                $("#country_id option:eq(1)").attr("selected", true);
            },
        },
        // Submit, to prove that it is not possible to continue without accepting the legal terms
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
            trigger: "a[href='/shop/confirm_order']",
        },
        // If I can proceed to payment, it's because the form validated fine
        {
            trigger: "div[name='o_checkbox_container'] input",
        },
        {
            trigger: ".btn-primary:contains('Pay Now')",
        },
        {
            trigger: '#payment_method label:contains("Dummy Provider")',
        },
        {
            trigger: 'button[name="o_payment_submit_button"]',
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
