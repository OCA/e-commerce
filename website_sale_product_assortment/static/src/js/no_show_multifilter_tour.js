/* Copyright 2021 Tecnativa - Carlos Roca
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
odoo.define("website_sale_product_assortment.tour_no_show_multifilter", function (
    require
) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a[href='/shop']",
            extra_trigger:
                ".o_wsale_product_grid_wrapper:has(a:contains('Test Product 1'))",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger:
                ".o_wsale_product_grid_wrapper:has(a:contains('Test Product 2'))",
        },
    ];

    tour.register(
        "test_assortment_with_no_show_multifilter",
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
