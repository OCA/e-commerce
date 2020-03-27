/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_show_stock_preview.tour", function(require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
    {
        trigger: "a:contains('Test Product 1')",
        extra_trigger: ".text-success:contains('In stock')"
    }
    ];
    tour.register(
        "website_sale_show_stock_preview",
        {
            url: "/shop",
            test: true,
            wait_for: base.ready(),
        },
        steps
    );
});
