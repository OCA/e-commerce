odoo.define("wbesite_sale_require_login.shop_buy", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "shop_buy_checkout_required_login_website",
        {
            test: true,
            url: "/shop",
        },
        [
            // Shop Page
            {
                // The first product is "Customizable Desk", and when the module `website_sale_product_configurator` is installed,
                // this product uses a configurator and requires a second step,
                // so we use another product instead.
                trigger: ".oe_product_cart a:contains('Warranty')",
            },
            // Product Page
            {
                trigger: "#add_to_cart",
            },
            {
                trigger: 'a[href="/shop/cart"]',
                extra_trigger: "sup.my_cart_quantity:contains('1')",
            },
            {
                trigger: '.oe_website_sale:not(a.btn-primary[href^="/shop/checkout"])',
                run: function () {
                    // Check: do nothing
                },
            },
            {
                trigger: '.oe_website_sale:not(a.btn-default[href^="/shop/checkout"])',
                run: function () {
                    // Check: do nothing
                },
            },
            // The End
        ]
    );
});
