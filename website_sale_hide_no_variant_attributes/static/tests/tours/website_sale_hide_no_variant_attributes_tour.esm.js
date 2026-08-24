// Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_hide_no_variant_attributes", {
    steps: () => [
        {
            content:
                "The informational (non-variant-defining) attribute must not be" +
                " rendered in the variant selector.",
            trigger:
                'ul.js_add_cart_variants:not(:has(li.variant_attribute[data-attribute-name="Test Material"]))',
        },
        {
            content: "The variant-defining attribute is rendered normally.",
            trigger:
                'li.variant_attribute[data-attribute-name="Test Size"] ' +
                'input[data-value-name="Large"]',
        },
        {
            content: "Select the size value excluded by the hidden material value.",
            trigger:
                'li.variant_attribute[data-attribute-name="Test Size"] ' +
                'input[data-value-name="Large"]',
            run: "click",
        },
        {
            content:
                "The selected size is not grayed out by the hidden material's" +
                " exclusion rule.",
            trigger:
                'li.variant_attribute[data-attribute-name="Test Size"] ' +
                'label:not(.css_not_available):has(input[data-value-name="Large"])',
        },
        {
            content: "Add the product to the cart.",
            trigger: "#add_to_cart",
            run: "click",
        },
        {
            content:
                "The product was added to the cart, confirming the hidden" +
                " material attribute never blocked Add to Cart.",
            trigger: "sup.my_cart_quantity:contains(1)",
        },
    ],
});
