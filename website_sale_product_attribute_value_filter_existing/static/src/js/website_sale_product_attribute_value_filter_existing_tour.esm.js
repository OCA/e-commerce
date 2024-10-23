/** @odoo-module **/

import {registry} from "@web/core/registry";

registry
    .category("web_tour.tours")
    .add("website_sale_product_attribute_value_filter_existing", {
        url: "/shop",
        steps: () => [
            // No product has the yellow colour attribute defined.
            // When enter to "/shop" the attribute "test yellow" should not appear in the list of filters by attribute.
            // For the following step it is checked that the attribute "test yellow" is
            // not present in the list but the attributes "test red", "test blue" and
            // "test green" must be present.
            {
                content:
                    "Ensure 'test red', 'test blue' and 'test green' attributes are present while 'Test yellow' is not.",
                trigger:
                    '#wsale_products_attributes_collapse:has(input[name="attribute_value"][title="Test red"]):has(input[name="attribute_value"][title="Test green"]):has(input[name="attribute_value"][title="Test blue"]):not(:has(input[name="attribute_value"][title="Test yellow"]))',
            },
        ],
    });
