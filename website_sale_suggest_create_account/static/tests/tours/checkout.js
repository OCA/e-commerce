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
            // Shop page
            {
                content: "select Acoustic Bloc Screens",
                trigger: ".oe_product_cart img",
                run: "click",
            },
            // Product page
            {
                content: "click add to cart",
                trigger: "#product_details #add_to_cart",
                run: "click",
            },
            // Cart
            {
                content: "check product is in cart, get cart id, logout, go to login",
                trigger: 'td.td-product_name:contains("Acoustic Bloc Screens")',
                run: function () {
                    window.location.href =
                        "/web/login?redirect=/shop/checkout?express=1";
                },
            },
            // TODO: Add a step to check that "checkout" button doesn't exists
            // Odoo 14.0 initial config doesn't have b2c actived for the website
            // Login Page
            {
                content: "fill login input",
                trigger: "#login",
                run: "text portal",
            },
            {
                content: "fill password input",
                trigger: "#password",
                run: "text portal",
            },
            {
                content: "click on login button",
                trigger: "button.btn-primary:first",
                run: "click",
            },
            // Checkout page
            {
                content: "check if payment button exists",
                trigger: "#o_payment_form_pay",
                run: function () {
                    // Do nothing, if payment button exists, checkout does not
                },
            },
        ]
    );
});
