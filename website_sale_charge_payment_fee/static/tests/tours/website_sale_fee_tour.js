// Copyright 2022 Studio73 - Miguel Gandía <miguel@studio73.es>
// License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
odoo.define("website_sale_charge_payment_fee.tour", function (require) {
    "use strict";
    var tour = require("web_tour.tour");
    const tourUtils = require("website_sale.tour_utils");

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
            id: "add_cart_step",
            content: "click on add to cart",
            extra_trigger: "label:contains(Steel) input:propChecked",
            trigger: '#product_detail form[action^="/shop/cart/update"] #add_to_cart',
        },
        {
            trigger: '.modal-footer button:contains("Continue Shopping")',
            extra_trigger: ".modal-content",
            content: "Click 'Continue Shopping' to close the modal and resume.",
            position: "bottom",
        },
        tourUtils.goToCart(),
        {
            content: "set three",
            extra_trigger: '#wrap:has(#cart_products tr:contains("Conference Chair"))',
            trigger: "#cart_products input.js_quantity",
            run: "text 3",
        },
        {
            content: "check amount",
            // Wait for cart_update_json to prevent concurrent update
            trigger: '#order_total .oe_currency_value:contains("99.00")',
        },
        {
            content: "go to checkout",
            extra_trigger: "#cart_products input.js_quantity:propValue(3)",
            trigger: 'a[href*="/shop/checkout"]',
        },
        {
            content: "Click the 'Next' button to proceed to the next step.",
            trigger: 'a:contains("Next")',
            position: "bottom",
        },
        {
            content: "Go to confirm order page",
            trigger: "a[href='/shop/confirm_order']",
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
            trigger: 'button[name="o_payment_submit_button"]:visible:not(:disabled)',
        },
        {
            content: "finish",
            trigger:
                '.oe_website_sale:contains("Please use the following transfer details")',
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
        },
        steps
    );
    return {
        steps: steps,
    };
});
