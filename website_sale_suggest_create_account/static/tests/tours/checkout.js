odoo.define("wbesite_sale_suggest_create_account.shop_buy", function (require) {
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
                trigger: "a.o_product_link:first",
            },
            // Product Page
            {
                trigger: "#add_to_cart",
            },
            // Go to cart
            {
                trigger: 'a[href="/shop/cart"]',
                extra_trigger: "sup.my_cart_quantity:contains('1')",
            },
            {
                trigger: 'a.btn-secondary[href^="/web/login"]:first',
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
            },
            // Checkout Page
            {
                trigger: "button[name='o_payment_submit_button']",
            },
            {
                trigger: "span",
                content: "Order",
            },
            // The End
        ]
    );
});
