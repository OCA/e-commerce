/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
registry
    .category("web_tour.tours")
    .add("website_sale_product_attribute_filter_category", {
        url: "/shop",
        steps: () => [
            {
                trigger: "a[href='/shop']",
                run: "click",
            },
            {
                trigger: ".js_attributes:has(strong:contains('Test category'))",
            },
            {
                trigger: "a:contains('Customizable Desk')",
                run: "click",
            },
            {
                trigger: "a[href='/shop']",
                run: "click",
            },
            // Span element must be available directly
            {
                trigger: "strong:contains('Test category')",
            },
            {
                trigger: "a:contains('Customizable Desk')",
                run: "click",
            },
        ],
    });
