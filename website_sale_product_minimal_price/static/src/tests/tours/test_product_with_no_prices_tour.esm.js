/* Copyright 2021 Carlos Roca
 * Copyright 2025 Carlos Lopez - Tecnativa
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
registry.category("web_tour.tours").add("test_product_with_no_prices", {
    url: "/shop",
    steps: () => [
        {
            trigger:
                ".oe_product_cart:has(.product_price:has(span:contains('From'))) a:contains('My product test with no prices')",
            content: "Product with label From",
        },
        {
            trigger: ".product_price:has(span:contains('10.00'))",
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger:
                ".oe_product_cart:has(.product_price:has(span:contains('10.00'))) a:contains('My product test')",
        },
        {
            trigger:
                ".oe_product_cart:has(.product_price:not(:has(span:contains('From'))):has(span:contains('20.00'))) a:contains('My product test no prices')",
            content: "Product without label From",
        },
    ],
});
