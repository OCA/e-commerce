/* Copyright 2024 Pilar Vargas
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_menu_partner_top_selling.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "#products_grid_before label:contains('My Regular Products')",
        },
        {
            trigger: "a:contains('Product 5')",
            extra_trigger:
                "#products_grid:has(a:contains('Product 3')):not(:has(a:contains('Product 1'))):not(:has(a:contains('Product 2'))):not(:has(a:contains('Product 4')))",
        },
    ];

    tour.register(
        "website_sale_menu_partner_top_selling",
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
