odoo.define(
    "website_sale_product_attribute_filter_visibility.tour",
    function (require) {
        "use strict";

        const tour = require("web_tour.tour");

        const steps = [
            {
                trigger: "a:contains('Filter Visibility Test Product 1')",
                extra_trigger: ".js_attributes:has(strong:contains('Test Color'))",
            },
            {
                trigger: "a:contains('Filter Visibility Test Product 1')",
                run: "click",
            },
            {
                trigger: "a[href='/shop']",
                extra_trigger: "#product_details:has(strong:contains('Test Color'))",
                run: "click",
            },
            {
                trigger: "a:contains('Filter Visibility Test Product 1')",
                extra_trigger: ".js_attributes:not(:has(strong:contains('Test Size')))",
            },
        ];

        tour.register(
            "website_sale_product_attribute_filter_visibility",
            {
                url: "/shop",
                test: true,
            },
            steps
        );
    }
);
