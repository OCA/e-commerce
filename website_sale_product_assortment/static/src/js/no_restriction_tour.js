/* Copyright 2021 Tecnativa - Carlos Roca
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
odoo.define("website_sale_product_assortment.tour_no_restriction", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a:contains('Test Product 1')",
        },
        {
            trigger: "a#add_to_cart",
        },
        {
            trigger: "a:contains('Test Product 1')",
            extra_trigger: "input.js_quantity[value='1']",
        },
    ];

    tour.register(
        "test_assortment_with_no_restriction",
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
