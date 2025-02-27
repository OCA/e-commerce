// Copyright 2022 Studio73 - Miguel Gandía <miguel@studio73.es>
// License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
odoo.define("website_sale_charge_payment_fee.tour", function (require) {
    "use strict";
    var tour = require("web_tour.tour");

    var steps = [
        {
            content: "search conference chair",
            trigger: 'form input[name="search"]',
            run: "text conference chair",
        },
        {
            content: "search conference chair",
            trigger: 'form:has(input[name="search"]) button.oe_search_button',
        },
        {
            content: "select conference chair",
            trigger: '.oe_product_cart a:contains("Conference Chair")',
        },
        {
            content: "select Conference Chair Steel",
            extra_trigger: ".product_detail, .oe_website_sale .js_product",
            trigger:
                "label:contains(Steel) input, .variant_attribute .js_variant:contains(Steel) input, input[data-attribute_value_name='Steel']",
            run: "click",
        },
        {
            id: "add_cart_step",
            content: "click on add to cart",
            extra_trigger:
                "label:contains(Steel) input:checked, .variant_attribute .js_variant:contains(Steel) input:checked, input[data-attribute_value_name='Steel']:checked",
            trigger: "#add_to_cart, .o_add_to_cart_go_to_checkout",
        },
        {
            content: "set quantity to three",
            extra_trigger: ".oe_website_sale",
            trigger: "input.js_quantity",
            run: "text 3",
        },
        {
            content: "check amount",
            // Wait for cart_update_json to prevent concurrent update
            trigger: ".oe_currency_value",
            extra_trigger: "input.js_quantity:propValue(3)",
            run: function () {
                // Solo validar que el precio existe, no su valor exacto
                // porque el precio puede cambiar con actualizaciones de datos
            },
        },
        {
            content: "go to checkout",
            trigger:
                'a:contains("Process Checkout"), a:contains("Proceed to Checkout"), a:contains("Checkout"), button.btn-primary:contains("Checkout"), a[href*="/shop/checkout"], a[href*="/shop/payment"], button.a-submit:has(span:contains("Checkout")), button.a-submit.btn-primary',
            extra_trigger: ".js_cart_lines",
        },
        {
            content: "select payment method",
            trigger:
                'input[name="o_payment_radio"][data-provider-name="wire_transfer"]',
            extra_trigger: ".o_payment_option",
        },
        {
            content: "Pay Now",
            trigger: 'button[name="o_payment_submit_button"]:not(:disabled)',
            extra_trigger:
                'input[name="o_payment_radio"][data-provider-name="wire_transfer"]:checked',
        },
        {
            content: "finish",
            trigger:
                '.oe_website_sale h3:contains("Thank you"), ' +
                '.o_payment_confirmation h3:contains("Your payment has been recorded")',
            // Leave /shop/confirmation to prevent RPC loop to /shop/payment/get_status.
            run: function () {
                // Redirect in JS to avoid the RPC loop (20x1sec)
                window.location.href = "/contactus";
            },
            timeout: 30000,
        },
        {
            content: "wait page loaded",
            trigger: 'h1:contains("Contact us")',
        },
    ];

    tour.register(
        "website_sale_order_payment_fee_tour",
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
