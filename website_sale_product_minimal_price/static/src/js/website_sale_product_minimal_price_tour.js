/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_product_minimal_price.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a:contains('My product test')",
            extra_trigger: ".product_price:has(span:contains('From '))",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger:
                ".js_attribute_value:eq(0):has(span:contains('Test v2'))",
        },
        {
            trigger: "a:contains('My product test')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: ".product_price:has(span:contains('125.00'))",
        },
    ];
    tour.register("website_sale_product_minimal_price",
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
