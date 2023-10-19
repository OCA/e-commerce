/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_checkout_skip_payment.tour", function (require) {
    "use strict";

    const tour = require("web_tour.tour");

    var steps = [
        {
            trigger: "a:contains('Customizable Desk')",
        },
        {
            trigger: "a#add_to_cart",
        },
        {
            trigger: "a[href='/shop/cart']",
            extra_trigger: "sup.my_cart_quantity:contains('1')",
        },
        {
            trigger: ".btn-primary:contains('Confirm')",
        },
        {
            trigger: ".btn:contains('Confirm')",
            extra_trigger: "b:contains('Billing & Shipping:')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "strong:contains('Payment Information:')",
        },
    ];
    tour.register(
        "website_sale_checkout_skip_payment",
        {
            url: "/shop",
            test: true,
        },
        steps
    );
    return {
        steps: steps,
    };
});
