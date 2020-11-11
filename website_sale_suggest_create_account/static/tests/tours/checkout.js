/* eslint-disable */
odoo.define("wbesite_sale_suggest_create_account.shop_buy", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "shop_buy_checkout_suggest_account_website",
        {
            test: true,
            url: "/shop?search=Acoustic Bloc Screens",
        },
        [
            {
                content: "select Acoustic Bloc Screens",
                trigger: '.oe_product_cart a:containsExact("Acoustic Bloc Screens")',
            },
            {
                id: "add_cart_step",
                content: "click on add to cart",
                trigger:
                    '#product_detail form[action^="/shop/cart/update"] .btn-primary',
            },
            {
                content: "check amount",
                // Wait for cart_update_json to prevent concurrent update
                trigger: '#order_total span.oe_currency_value:contains("2,950.00")',
                run: function () {}, // It's a check
            },
            {
                content: "products into cart",
                trigger: "#cart_products input.js_quantity",
                run: "text 1",
            },
            {
                content: "suggest to login user",
                trigger: 'a[href="/web/login?redirect=/shop/checkout?express=1"]',
            },
            {
                trigger: "#login",
                run: "text portal",
            },
            {
                trigger: "#password",
                run: "text portal",
            },
            {
                trigger: "button.btn-primary:first",
                run: "click",
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
                    window.location.href = "/contactus"; // Redirect in JS to avoid the RPC loop (20x1sec)
                },
                timeout: 30000,
            },
        ]
    );
});
