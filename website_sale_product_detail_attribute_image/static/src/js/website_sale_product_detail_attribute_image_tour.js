/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_product_detail_attribute_image.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a:contains('Customizable Desk')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: ".product-detail-attributes:has(span:contains('Policy One Value 1')):not(:has(span:contains('Dangerousness'))):has(span:contains('Policy One Value 1 for website'))",
        },
    ];
    tour.register("website_sale_product_detail_attribute_image",
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
