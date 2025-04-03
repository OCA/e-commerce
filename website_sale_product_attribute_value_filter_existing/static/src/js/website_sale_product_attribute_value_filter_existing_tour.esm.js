/** @odoo-module **/

import {registry} from "@web/core/registry";

registry
    .category("web_tour.tours")
    .add("website_sale_product_attribute_value_filter_existing", {
        test: true,
        url: "/shop",
        steps: () => [
            // No product has the yellow colour attribute defined.
            // When enter to "/shop" the attribute "test yellow" should not appear in the list of filters by attribute.
            // For the following steps it is checked that the attribute "test yellow" is
            // not present in the list but the attributes "test red", "test blue" and
            // "test green" must be present.
            {
                content:
                    "Ensure 'test red', 'test blue' and 'test green' attributes are present while 'Test yellow' is not.",
                trigger: "body",
                extra_trigger:
                    ".js_attributes:not(:contains('Test yellow')):has(label:contains('Test red')), .js_attributes:not(:contains('Test yellow')):has(label:contains('Test blue')), .js_attributes:not(:contains('Test yellow')):has(label:contains('Test green'))",
            },
            {
                content: "Selecting the 'test green' attribute.",
                trigger:
                    ".form-check:has(label:contains('Test green')) input[type='checkbox']",
                run: "click",
            },
            // After selecting, the attributes "test red" and "test green" must be present.
            // "Test yellow" should not be present as it is not used in any product and
            // "test blue" should not be present as it is not used in the products shown.
            {
                content:
                    "Ensure 'test red' and 'test green' attributes are present while 'Test yellow' and 'test blue' are not.",
                trigger: "body",
                extra_trigger:
                    ".js_attributes:not(:contains('Test blue')):not(:contains('Test yellow')):has(label:contains('Test green')), .js_attributes:not(:contains('Test blue')):not(:contains('Test yellow')):has(label:contains('Test red'))",
            },
        ],
    });
