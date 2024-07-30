odoo.define("website_sale_checkout_skip_payment.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    const tourUtils = require("website_sale.tour_utils");

    tour.register(
        "website_sale_checkout_skip_payment",
        {
            test: true,
            url: "/shop?search=Storage%20Box",
        },
        [
            {
                content: "select Storage Box",
                extra_trigger: ".oe_search_found",
                trigger: '.oe_product_cart a:contains("Storage Box")',
            },
            {
                content: "Add Storage Box into cart",
                trigger: "a:contains(ADD TO CART)",
            },
            tourUtils.goToCart(),
            {
                content: "go to checkout",
                extra_trigger: "#cart_products input.js_quantity:propValue(1)",
                trigger: 'a[href*="/shop/checkout"]',
            },
            {
                trigger: '.btn-primary:contains("Confirm")',
            },
            {
                trigger: ".btn:contains('Confirm')",
                extra_trigger: "b:contains('Billing & Shipping:')",
            },
            {
                trigger: "a[href='/shop']",
                extra_trigger: "strong:contains('Payment Information:')",
            },
            {
                content: "Check confirmation and that the cart has been left empty",
                trigger: "a:has(.my_cart_quantity:containsExact(0))",
                extra_trigger: "strong:contains('Payment Information:')",
            },
        ]
    );
});
