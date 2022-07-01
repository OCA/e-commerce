/* Copyright 2021 Tecnativa - Carlos Roca
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
odoo.define("website_sale_product_assortment.tour_no_purchase", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger:
                ".o_wsale_product_information_text:has(.text-danger:has(.fa-exclamation-triangle)) a:contains('Test Product 1')",
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
            wait_for: base.ready(),
        },
        steps
    );
    return {
        steps: steps,
    };
});
