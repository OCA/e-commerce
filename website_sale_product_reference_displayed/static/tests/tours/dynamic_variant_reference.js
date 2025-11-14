odoo.define(
    "website_sale_product_reference_displayed.tour_dynamic_variant_reference",
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        tour.register(
            "tour_dynamic_variant_reference",
            {
                test: true,
                url: "/shop?search=Test dynamic variant product template",
            },
            [
                {
                    content: "Select Product",
                    trigger:
                        '.oe_product_cart a:containsExact("Test dynamic variant product template")',
                },
                {
                    content: "Click on the first attribute value",
                    trigger:
                        'input[data-attribute_name="Test dynamic variant attribute"][data-value_name="Test dynamic variant value 1"]',
                },
                {
                    content: "Wait for variant to be loaded",
                    trigger: '.oe_price .oe_currency_value:contains("0.00")',
                    // eslint-disable-next-line no-empty-function
                    run: function () {},
                },
                {
                    content: "Check the Internal Reference of the 1st variant",
                    trigger: "span.js_variant_reference_displayed:contains(TESTREF1)",
                },
                {
                    content: "Click on the second attribute value",
                    trigger:
                        'input[data-attribute_name="Test dynamic variant attribute"][data-value_name="Test dynamic variant value 2"]',
                },
                {
                    content: "Wait for variant to be loaded",
                    trigger: '.oe_price .oe_currency_value:contains("0.00")',
                    // eslint-disable-next-line no-empty-function
                    run: function () {},
                },
                {
                    content: "Check the Internal Reference of the 2st variant",
                    trigger: "span.js_variant_reference_displayed:contains(TESTREF2)",
                },
            ]
        );
    }
);
