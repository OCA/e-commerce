/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_stock_list_preview.tour", function(require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a:contains('Test Product 1')",
            extra_trigger: ".text-success:contains('30  available')",
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: "a:contains('Test Product 2')",
            extra_trigger: ".text-success:contains('In stock')",
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: "a:contains('Test Product 3')",
            extra_trigger: ".text-warning:contains('5  available')",
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: "a:contains('Test Product 4')",
            extra_trigger: ".text-success:contains('test message')",
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: "a:contains('Test Product 5')",
            //            Extra_trigger: ".text-success:contains('30  available')",
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: "a:contains('Test Product 6')",
            extra_trigger: ".text-danger:contains(' Temporarily out of stock')",
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: "a:contains('Test Product 7')",
            extra_trigger: ".text-danger:contains(' Temporarily out of stock')",
        },
    ];

    tour.register(
        "website_sale_stock_list_preview",
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
