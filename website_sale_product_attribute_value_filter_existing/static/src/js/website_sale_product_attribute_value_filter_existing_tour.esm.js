/** @odoo-module **/

import tour from "web_tour.tour";

tour.register(
    "website_sale_product_attribute_value_filter_existing",
    {
        test: true,
        url: "/shop",
    },
    // No product has the yellow colour attribute defined.
    // When enter to "/shop" the attribute "test yellow" should not appear in the list of filters by attribute.
    [
        // For the following steps it is checked that the attribute "test yellow" is
        // not present in the list but the attributes "test red", "test blue" and
        // "test green" must be present.
        {
            content:
                "Search a product. Ensure 'test red', 'test blue' and 'test green' attributes are present while 'Test yellow' is not.",
            trigger: "form input[name=search]",
            run: "text desk",
            extra_trigger:
                ".js_attributes:not(:contains('Test yellow')):has(label:contains('Test red')), .js_attributes:not(:contains('Test yellow')):has(label:contains('Test blue')), .js_attributes:not(:contains('Test yellow')):has(label:contains('Test green'))",
        },
        {
            content:
                "Submit search button. Ensure 'test red', 'test blue' and 'test green' attributes are present while 'Test yellow' is not.",
            trigger: 'form:has(input[name="search"]) .oe_search_button',
            extra_trigger:
                ".js_attributes:not(:contains('Test yellow')):has(label:contains('Test red')), .js_attributes:not(:contains('Test yellow')):has(label:contains('Test blue')), .js_attributes:not(:contains('Test yellow')):has(label:contains('Test green'))",
        },
        // After searching, the attributes "test red" and "test green" must be present.
        // "Test yelow" should not be present as it is not used in any product and
        // "test blue" should not be present as it is not used in the products shown.
        {
            content:
                "Go to /shop after the search. Ensure 'test red' and 'test green' attributes are present while 'Test yellow' and 'test blue' are not.",
            trigger: "a[href='/shop']",
            extra_trigger:
                ".js_attributes:not(:contains('Test blue'), :contains('Test yellow')):has(label:contains('Test green')), .js_attributes:not(:contains('Test blue'), :contains('Test yellow')):has(label:contains('Test red'))",
        },
    ]
);
