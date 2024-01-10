odoo.define("website_sale_wishlist_hide_price.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "website_sale_wishlist_hide_price_tour",
        {
            url: "/shop",
            test: true,
        },
        [
            {
                trigger: ".oe_product_cart:contains('Customizable') .o_add_wishlist",
            },
            {
                trigger: "a[href='/shop/wishlist']",
            },
            {
                trigger:
                    "tr:has(a:contains('Customizable Desk')):not(:has(button.o_wish_add)):not(:has(span.oe_currency_value))",
            },
        ]
    );
});
