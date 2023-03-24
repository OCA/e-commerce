/** @odoo-module **/

import tour from "web_tour.tour";

tour.register(
    "website_sale_product_attribute_value_filter_existing",
    {
        test: true,
        url: "/shop",
    },
    [
        {
            content: "1: browse shop page",
            trigger: "a[href='/shop']",
        },
        {
            content: "2: search a product",
            trigger: "input[name=search]",
            run: "text Ipod",
            extra_trigger: ".js_attributes:has(label:contains('Test blue'))",
        },
        {
            content: "3: submit search button",
            trigger: ".oe_search_button",
            extra_trigger: ".js_attributes:has(label:contains('Test blue'))",
        },
        {
            content: "4: browse shop page after search",
            trigger: "a[href='/shop']",
            extra_trigger: ".js_attributes:not(:has(label:contains('Test blue')))",
        },
    ]
);
