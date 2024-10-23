/** @odoo-module **/

import {registry} from "@web/core/registry";

registry
    .category("web_tour.tours")
    .add("website_sale_product_attribute_value_filter_existing_search_desk", {
        url: "/shop?search=customizable",
        steps: () => [
            // After searching, the attributes "test red" and "test green" must be present.
            // "Test yelow" should not be present as it is not used in any product and
            // "test blue" should not be present as it is not used in the products shown.
            {
                content:
                    "Ensure 'test red' and 'test green' attributes are present while 'Test yellow' and 'test blue' are not.",
                trigger:
                    '#wsale_products_attributes_collapse:has(input[name="attribute_value"][title="Test red"]):has(input[name="attribute_value"][title="Test green"]):not(:has(input[name="attribute_value"][title="Test blue"])):not(:has(input[name="attribute_value"][title="Test yellow"]))',
            },
        ],
    });
