/* Copyright 2019 Sergio Teruel
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

odoo.define("website_sale_product_attribute_value_filter_existing.tour", function (require) {
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
            trigger: 'input[name=search]',
            run: 'text Ipod',
            extra_trigger: ".js_attributes:has(span:contains('Test blue'))",
        },
        {
            trigger: '.oe_search_button',
            extra_trigger: ".js_attributes:has(span:contains('Test blue'))",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "li:not(:has(span:contains('Test blue')))",
        },
    ];
    tour.register("website_sale_product_attribute_value_filter_existing",
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
