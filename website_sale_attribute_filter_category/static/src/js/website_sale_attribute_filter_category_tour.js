/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_attribute_filter_category.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: "a:contains('Customizable Desk')",
            extra_trigger: ".js_attributes:has(span:contains('Test category'))",
        },
        {
            trigger: "a[href='/shop']",
        },
        // span element must be available directly
        {
            trigger: "a:contains('Customizable Desk')",
            extra_trigger: "span:contains('Test category')",
        },
    ];
    tour.register("website_sale_attribute_filter_category",
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
