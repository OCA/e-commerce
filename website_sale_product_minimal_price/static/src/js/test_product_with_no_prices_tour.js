/* Copyright 2021 Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("test_product_with_no_prices.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a:contains('My product test with no prices')",
            extra_trigger: ".product_price:has(span:contains('From'))",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: ".product_price:has(span:contains('10.00'))",
        },
        {
            trigger: "a:contains('My product test')",
            extra_trigger: ".product_price:has(span:contains('10.00'))",
        },
    ];
    tour.register(
        "test_product_with_no_prices",
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
