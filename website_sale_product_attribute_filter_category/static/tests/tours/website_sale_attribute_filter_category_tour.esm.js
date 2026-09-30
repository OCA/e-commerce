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
                expectUnloadPage: true,
            },
            {
                trigger: ".js_attributes:has(b:contains('Test category'))",
            },
            {
                trigger: "a:contains('Customizable Desk')",
                run: "click",
                expectUnloadPage: true,
            },
            {
                trigger: "a[href='/shop']",
                run: "click",
                expectUnloadPage: true,
            },
            // Span element must be available directly
            {
                trigger: "b:contains('Test category')",
            },
            {
                trigger: "a:contains('Customizable Desk')",
                run: "click",
                expectUnloadPage: true,
            },
        ],
    });
