/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_init_category.tour", function(require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "#products_grid_before:not(:has(a:contains('All Products')))",
            extra_trigger: "#products_grid_before a:contains('Init Category')",
        },
    ];

    tour.register(
        "website_sale_init_category",
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
