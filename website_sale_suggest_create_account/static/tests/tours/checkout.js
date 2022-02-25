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
                content: "click add to cart",
                trigger: "#product_details #add_to_cart",
            },
            {
                content: "check product is in cart, get cart id, logout, go to login",
                trigger: 'td.td-product_name:contains("Acoustic Bloc Screens")',
                run: function () {
                    window.location.href = "/web/login";
                },
            },
            // TODO: Add a step to check that "checkout" button doesn't exists
            // Odoo 14.0 initial config doesn't have b2c actived for the website
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
        ]
    );
});
