/** @odoo-module */
/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
registry.category("web_tour.tours").add("website_sale_secondary_unit", {
    test: true,
    url: "/shop",
    steps: () => [
        {
            trigger: "a:contains('Test product')",
        },
        {
            trigger: "#secondary_uom",
            run: "text(Box 5 Units)",
        },
        {
            trigger: "#add_to_cart",
            extra_trigger:
                ".js_product:has(input[name='add_qty']:propValueContains(5)):has(.price_uom)",
        },
        {
            trigger: "a[href='/shop/cart']",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "span:contains(Box 5 Units)",
        },
        {
            trigger: "a:contains('Test product')",
        },
        {
            trigger: "#add_to_cart",
            extra_trigger:
                ".js_product:has(input[name='add_qty']:propValueContains(1))",
        },
        {
            trigger: "a[href='/shop/cart']",
        },
        {
            trigger: "a[href='/shop/checkout?express=1']",
            extra_trigger: "span:containsExact(Units)",
        },
        {
            trigger: "div[id='o_wsale_total_accordion'] button.accordion-button",
        },
        {
            trigger: "h6[name='secondary_uom_qty'] span:containsExact(Box 5)",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "table:has(span:contains(Box 5)):has(span:contains(Units))",
        },
    ],
});
