/* Copyright 2020 Alexandre D. Díaz
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_product_item_cart_custom_qty.tour", function(require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger:
                ".o_wsale_product_information:has(a:contains('Test Product')) a[title='Add one']",
        },
        {
            trigger:
                ".o_wsale_product_information:has(a:contains('Test Product')) a[title='Shopping cart']",
        },
        {
            trigger: ".js_delete_product",
            extra_trigger:
                "tr:has(a:has(strong:contains('Test Product'))) .js_quantity[value='2']",
        },
    ];
    tour.register(
        "website_sale_product_item_cart_custom_qty",
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
