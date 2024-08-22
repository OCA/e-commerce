/* Copyright 2021 Tecnativa - Carlos Roca
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
odoo.define("website_sale_product_assortment.tour_no_purchase", function (require) {
    var tour = require("web_tour.tour");

    var steps = [
        {
            trigger:
                ".oe_product_cart:has(.text-danger:has(.fa-exclamation-triangle)) a:contains('Test Product 1')",
        },
        {
            trigger: "a#add_to_cart.disabled",
            extra_trigger: ".text-danger:has(.fa-exclamation-triangle)",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "span[name='testing']",
        },
    ];

    tour.register(
        "test_assortment_with_no_purchase",
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
