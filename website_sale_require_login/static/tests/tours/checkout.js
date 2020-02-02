odoo.define("wbesite_sale_require_login.shop_buy", function(require) {
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
                trigger: 'a[href^="/shop/product/"]:first',
                run: "click",
            },
            // Product Page
            {
                trigger: "#add_to_cart",
                run: "click",
            },
            {
                trigger: '.oe_website_sale:not(a.btn-primary[href^="/shop/checkout"])',
                run: function() {
                    // Check: do nothing
                },
            },
            {
                trigger: '.oe_website_sale:not(a.btn-default[href^="/shop/checkout"])',
                run: function() {
                    // Check: do nothing
                },
            },
            // The End
        ]
    );
});
