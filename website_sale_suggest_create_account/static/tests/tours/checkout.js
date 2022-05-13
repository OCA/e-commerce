odoo.define("wbesite_sale_suggest_create_account.shop_buy", function(require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "shop_buy_checkout_suggest_account_website",
        {
            test: true,
            url: "/shop",
        },
        [
            // Shop Page
            {
                trigger: 'a[href^="/shop/product/"]:first',
                run: "click",
            },
            // Product Page
            {
                trigger: "#add_to_cart",
                run: "click",
            },
            {
                trigger: 'a.btn-secondary[href^="/web/login"]:first',
                run: function() {
                    // Check: do nothing
                },
            },
            {
                trigger: 'a.btn-primary[href^="/web/login"]:first',
                run: "click",
            },
            // TODO: Add a step to check that "checkout" button doesn't exists
            // Odoo 13.0 initial config doesn't have b2c actived for the website
            // Login Page
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
            // Checkout Page
            {
                trigger: "#o_payment_form_pay",
                run: "click",
            },
            {
                trigger: "span",
                content: "Order",
            },
            // The End
        ]
    );
});
