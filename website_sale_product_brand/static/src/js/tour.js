/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_product_brand.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    var steps = [
        {
            trigger: "a[href='/page/product_brands']",
            content: "Go to 'Product brand' page",
            position: "bottom",
        },
        {
            content: "search Apple",
            trigger: 'form input[name="search"]',
            run: "text Apple",
            position: "bottom",
        },
        {
            content: "Click to search Apple",
            trigger: 'form:has(input[name="search"]) button',
            position: "bottom",
        },
        {
            content: "select Apple",
            trigger: 'section a div:contains("Apple")',
        },
    ];

    tour.register(
        "website_sale_product_brand",
        {
            url: "/",
            test: true,
        },
        steps
    );
});
