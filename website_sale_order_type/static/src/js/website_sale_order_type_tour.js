/* Copyright 2020 Tecnativa - João Marques
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_order_type.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: ".oe_product_cart a:contains('Customizable')",
        },
        {
            trigger: "#add_to_cart",
        },
        {
            trigger: ".btn:contains('Process Checkout')",
        },
    ];
    tour.register(
        "website_sale_order_type_tour",
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
