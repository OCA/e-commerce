/** @odoo-module */
/* Copyright 2021 Carlos Roca
 * Copyright 2025 Carlos Lopez - Tecnativa
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
registry.category("web_tour.tours").add("test_product_with_no_prices", {
    url: "/shop",
    test: true,
    steps: () => [
        {
            trigger: "a:contains('My product test with no prices')",
            extra_trigger: ".product_price:has(span:contains('From'))",
            content: "Product with label From",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: ".product_price:has(span:contains('10.00'))",
        },
        {
            trigger: "a:contains('My product test')",
            extra_trigger: ".product_price:has(span:contains('10.00'))",
        },
        {
            trigger: "a:contains('My product test no prices')",
            extra_trigger:
                ".product_price:not(:has(span:contains('From'))):has(span:contains('20.00'))",
            content: "Product without label From",
        },
    ],
});
