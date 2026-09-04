/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
registry.category("web_tour.tours").add("website_sale_secondary_unit", {
    url: "/shop",
    steps: () => [
        {
            trigger: "a:contains('Test product')",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: 'select[name="secondary_uom_id"]',
            run: "selectByLabel Box 5 Units",
        },
        {
            trigger: 'input[name="add_qty"]',
            run: "edit 2",
        },
        {
            trigger: "#add_to_cart",
            run: "click",
        },
        // The notification counts secondary units.
        {
            trigger: ".o_cart_item_count:contains('2')",
        },
        {
            trigger: "a[href='/shop/cart']",
            run: "click",
            expectUnloadPage: true,
        },
        // The line is sold in boxes: 2 boxes of 5 units = 10 units.
        {
            trigger:
                ".o_cart_product:contains('Box 5 Units'):contains('= 10 Units') input.js_quantity[value='2']",
        },
        // Buying the same product in its own unit of measure adds a new line.
        {
            trigger: "a[href='/shop']",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "a:contains('Test product')",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "#add_to_cart",
            run: "click",
        },
        // The cart counts secondary units: 2 boxes + 1 unit.
        {
            trigger: ".my_cart_quantity:contains('3')",
        },
        {
            trigger: "a[href='/shop/cart']",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger:
                ".o_cart_product:contains('Box 5 Units'):has(input.js_quantity[value='2'])",
        },
        {
            trigger: ".o_cart_product:has(input.js_quantity[value='1'])",
        },
        // Quantities are increased by secondary unit.
        {
            trigger:
                ".o_cart_product:contains('Box 5 Units') .css_quantity a:has(.oi-plus)",
            run: "click",
        },
        {
            trigger:
                ".o_cart_product:contains('Box 5 Units'):contains('= 15 Units'):has(input.js_quantity[value='3'])",
        },
        {
            trigger: ".my_cart_quantity:contains('4')",
        },
        // The checkout summary shows the secondary unit too.
        {
            trigger: "a[name='website_sale_main_button']",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger:
                "td[name='website_sale_cart_summary_product_name']:contains('Box 5 Units')",
        },
    ],
});
