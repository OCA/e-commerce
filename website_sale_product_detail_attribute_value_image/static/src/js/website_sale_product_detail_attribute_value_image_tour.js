/* Copyright 2020 Alexandre D. Díaz
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_product_detail_attribute_value_image.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a:contains('Customizable Desk')",
        },
        {
            trigger: "*",
            extra_trigger: ".product-detail-attributes-values:has(span:contains('Policy One Value 1 for website'))",
        },
        {
            trigger: "*",
            extra_trigger: ".product-detail-attributes-values:not(:has(span:contains('High dangerousness')))",
        },
        {
            trigger: "*",
            extra_trigger: ".product-detail-attributes-values:has(span:contains('Policy Two Value 1'))",
        },
    ];
    tour.register("website_sale_product_detail_attribute_value_image",
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
