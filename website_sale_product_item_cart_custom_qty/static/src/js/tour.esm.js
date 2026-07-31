/* Copyright 2020 Alexandre D. Díaz
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_product_item_cart_custom_qty", {
    url: "/shop",
    steps: () => [
        {
            trigger: ".oe_product_cart:contains('Test Product')",
            run: "hover",
        },
        {
            trigger:
                ".oe_product_cart:contains('Test Product') a[title='Add one']:not(:visible), .oe_product_cart:contains('Test Product') a[title='Add one']",
            run: "click",
        },
        {
            trigger:
                ".oe_product_cart:contains('Test Product') button[title='Add to cart'], .oe_product_cart:contains('Test Product') a[title='Add to cart']",
            run: "click",
        },
        {
            trigger: ".my_cart_quantity:contains('2')",
        },
        {
            trigger: 'a[href="/shop/cart"]',
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: ".o_cart_product:contains('Test Product') input.js_quantity",
        },
        {
            trigger: ".js_delete_product",
            run: "click",
        },
    ],
});
