/* Copyright 2019 Sergio Teruel
 * Copyright 2025 Carlos Lopez - Tecnativa
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
registry.category("web_tour.tours").add("website_sale_product_minimal_price", {
    url: "/shop",
    test: true,
    steps: () => [
        {
            trigger:
                ".o_wsale_product_information:has(span:contains('From')) a:contains('My product test with various prices')",
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: "a:contains('My product test with various prices')",
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: ".product_price:has(span:contains('125.00'))",
        },
    ],
});
