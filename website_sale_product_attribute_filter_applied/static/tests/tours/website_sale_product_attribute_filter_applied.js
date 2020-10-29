odoo.define("website_sale_product_attribute_filter_applied.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "website_sale_product_attribute_filter_applied",
        {
            test: true,
            url: "/shop",
        },
        [
            {
                content: "Apply 'Cabernet Sauvignon' attribute filter",
                trigger:
                    '.js_attributes label:contains("Cabernet Sauvignon") input[type="checkbox"]',
            },
            {
                content: "Filter is listed and we can remove it",
                trigger:
                    '#wsale_products_attributes_filters_applied span:contains("Cabernet Sauvignon") + label',
            },
            {
                content: "Check that the applied filters are not shown",
                trigger: "body:not(:has(#wsale_products_attributes_filters_applied))",
                run: function () {
                    return true;
                },
            },
        ]
    );
});
