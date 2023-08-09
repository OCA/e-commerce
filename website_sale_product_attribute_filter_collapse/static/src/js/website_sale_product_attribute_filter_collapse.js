/* Copyright 20223 Tecnativa - Pilar Vargas
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_product_attribute_filter_collapse.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    var steps = [
        {
            trigger: "a:contains('Test a1')",
        },
        {
            trigger: "div:contains('Test v1')",
        },
        {
            trigger: "a:contains('Customizable')",
        },
        {
            trigger: "#add_to_cart",
        },
        {
            trigger: "button:contains('Proceed to Checkout')",
        },
        {
            trigger: ".btn-primary:contains('Process Checkout')",
        },
    ];
    tour.register(
        "website_sale_product_attribute_filter_collapse",
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
