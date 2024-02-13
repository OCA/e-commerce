// Copyright 2022 Studio73 - Miguel Gandía <miguel@studio73.es>
// License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
odoo.define("website_sale_charge_payment_fee.tour", function (require) {
    "use strict";
    var tour = require("web_tour.tour");
    var base = require("web_editor.base");
    var steps = [
        {
            content: "search conference chair",
            trigger: 'form input[name="search"]',
            run: "text conference chair",
        },
        {
            content: "search conference chair",
            trigger: 'form:has(input[name="search"]) .oe_search_button',
        },
        {
            content: "select conference chair",
            trigger: '.oe_product_cart:first a:contains("Conference Chair")',
        },
        {
            content: "select Conference Chair Steel",
            extra_trigger: "#product_detail",
            trigger: "label:contains(Steel) input",
        },
        {
            id: "add_cart_step",
            content: "click on add to cart",
            extra_trigger: "label:contains(Steel) input:propChecked",
            trigger: '#product_detail form[action^="/shop/cart/update"] .btn-primary',
        },
        {
            content: "set three",
            extra_trigger: '#wrap:not(:has(#cart_products tr:contains("Storage Box")))',
            trigger: "#cart_products input.js_quantity",
            run: "text 3",
        },
        {
            content: "check amount",
            // Wait for cart_update_json to prevent concurrent update
            trigger: '#order_total span.oe_currency_value:contains("49.50")',
        },
        {
            content: "go to checkout",
            extra_trigger: "#cart_products input.js_quantity:propValue(3)",
            trigger: 'a[href*="/shop/checkout"]',
        },
        {
            content: "select payment",
            trigger: '#payment_method label:contains("Wire Transfer")',
        },
        {
            content: "Pay Now",
            // Either there are multiple payment methods, and one is checked, either there is only one, and therefore there are no radio inputs
            extra_trigger:
                '#payment_method label:contains("Wire Transfer") input:checked,#payment_method:not(:has("input:radio:visible"))',
            trigger: 'button[id="o_payment_form_pay"]:visible:not(:disabled)',
        },
        {
            content: "finish",
            trigger: '.oe_website_sale:contains("Please make a payment to:")',
            // Leave /shop/confirmation to prevent RPC loop to /shop/payment/get_status.
            // The RPC could be handled in python while the tour is killed (and the session), leading to crashes
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
        "website_sale_order_payment_acquirer_tour",
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
