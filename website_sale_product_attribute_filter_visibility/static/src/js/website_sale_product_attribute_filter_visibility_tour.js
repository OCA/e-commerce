/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_product_attribute_filter_visibility.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a:contains('Customize')",
        },
        {
            trigger: "a:contains('Product Attribute')",
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: "a:contains('iPod')",
            extra_trigger: ".js_attributes:has(strong:contains('Test Color'))",
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: "a:contains('iPod')",
            extra_trigger: ".js_attributes:not(:has(strong:contains('Test Size')))",
        },
    ];
    tour.register("website_sale_product_attribute_filter_visibility",
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
