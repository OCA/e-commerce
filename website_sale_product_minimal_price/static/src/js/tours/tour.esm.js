/** @odoo-module **/

/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("test_website_sale_product_minimal_price", {
    url: "/shop",
    test: true,
    steps: () => [
        {
            trigger:
                ".o_wsale_product_information:has(span:contains('From')) a:contains('My product test with various prices')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: ".js_add_cart_variants:has(span:contains('Test v2'))",
        },
        {
            trigger: "a:contains('My product test with various prices')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: ".product_price:has(span:contains('125.00'))",
        },
    ],
});
