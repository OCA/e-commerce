/* Copyright 2020 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_stock_force_block.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a:contains('Computer Motherboard')",
            extra_trigger: ".product_price:not(:has(a))",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "#add_to_cart.disabled",
        },

    ];
    tour.register("website_sale_stock_force_block",
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
