/* Copyright 2020 Alexandre D. Díaz
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_product_item_cart_custom_qty.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    var steps = [
        {
            trigger:
                ".o_wsale_product_information_text:has(a:contains('Test Product'))",
            extra_trigger: " a[title='Add one']",
        },
        {
            trigger:
                ".o_wsale_product_information_text:has(a:contains('Test Product'))",
            extra_trigger: " a[title='Remove one']",
        },
        {
            trigger:
                ".o_wsale_product_information_text:has(a:contains('Test Product'))",
            extra_trigger: " a[title='Shopping cart']",
        },

        {
            trigger:
                ".o_wsale_product_information_text:has(a:contains('Test Product'))",
            extra_trigger: ".js_quantity[value='1']",
        },
    ];
    tour.register(
        "website_sale_product_item_cart_custom_qty",
        {
            url: "/shop",
            test: true,
        },
        steps
    );
    return {
        steps: steps,
    };
});
