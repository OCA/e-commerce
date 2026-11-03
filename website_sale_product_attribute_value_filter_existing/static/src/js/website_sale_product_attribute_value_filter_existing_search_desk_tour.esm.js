import {registry} from "@web/core/registry";

registry
    .category("web_tour.tours")
    .add("website_sale_product_attribute_value_filter_existing_search_desk", {
        steps: () => [
            // After searching for "Alpha", only that product is listed. Its values
            // "test red" and "test green" must be present; "test blue" must not, since
            // it is only used by "Beta", and "Test yellow" is used by no product.
            {
                content:
                    "Ensure 'test red' and 'test green' attributes are present while 'Test yellow' and 'test blue' are not.",
                trigger:
                    '#wsale_products_attributes_collapse:has(input[name="attribute_value"][title="Test red"]):has(input[name="attribute_value"][title="Test green"]):not(:has(input[name="attribute_value"][title="Test blue"])):not(:has(input[name="attribute_value"][title="Test yellow"]))',
            },
        ],
    });
