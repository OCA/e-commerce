/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_product_minimal_price.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger:
                ".o_wsale_product_information:has(span:contains('From')) a:contains('My product test with various prices')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: ".js_add_cart_variants:has(span:contains('Test v2'))",
        },
        {
            trigger: "a:contains('My product test with various prices')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: ".product_price:has(span:contains('125.00'))",
        },
    ];

    tour.register(
        "website_sale_product_minimal_price",
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
