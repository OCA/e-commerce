// Copyright 2022 Studio73 - Miguel Gandía <miguel@studio73.es>
// License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
odoo.define("website_sale_charge_payment_fee.tour", function (require) {
    "use strict";
    var tour = require("web_tour.tour");

    tour.register(
        "website_sale_order_payment_fee_tour",
        {
            test: true,
            url: "/shop",
        },
        [
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
                trigger:
                    '#product_detail form[action^="/shop/cart/update"] #add_to_cart',
            },
            {
                trigger: "button:contains('Proceed to Checkout')",
            },
            {
                content: "go to checkout",
                trigger: 'a[href*="/shop/checkout?express=1"]',
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
                trigger:
                    'button[name="o_payment_submit_button"]:visible:not(:disabled)',
            },
            {
                content: "finish",
                trigger:
                    '.oe_website_sale:contains("Please use the following transfer details")',
                run: function () {
                    window.location.href = "/contactus";
                },
                timeout: 30000,
            },
            {
                content: "wait page loaded",
                trigger: 'h1:contains("Contact us")',
            },
        ]
    );
});
