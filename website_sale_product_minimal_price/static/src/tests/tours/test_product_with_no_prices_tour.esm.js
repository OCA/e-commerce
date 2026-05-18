/* Copyright 2021 Carlos Roca
 * Copyright 2025 Carlos Lopez - Tecnativa
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
registry.category("web_tour.tours").add("test_product_with_no_prices", {
    url: "/shop",
    test: true,
    steps: () => [
        {
            trigger:
                ".oe_product_cart:has(a:contains('My product test with no prices')) .product_price span",
            content: "Variant product is listed with a rendered price",
        },
        {
            trigger:
                ".oe_product_cart:has(a:contains('My product test no prices')) .product_price span",
        },
        {
            trigger:
                ".oe_product_cart:has(a:contains('My product test with no prices')) a:contains('My product test with no prices')",
            content: "Variant product link is accessible",
        },
    ],
});
