/* Copyright 2020 Alexandre D. Díaz
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_product_item_cart_custom_qty", {
    url: "/shop",
    steps: () => [
        {
            trigger:
                ".o_wsale_product_information:contains('Test Product') a[title='Add one']",
            run: "click",
        },
        {
            trigger:
                ".o_wsale_product_information:contains('Test Product') a[title='Shopping cart']",
            run: "click",
        },
        {
            trigger: "sup.my_cart_quantity:contains('2')",
        },
        {
            trigger: 'a[href="/shop/cart"]',
            run: "click",
        },
        {
            trigger: ".o_cart_product:contains('Test Product') .js_quantity[value='2']",
        },
        {
            trigger: ".js_delete_product",
            run: "click",
        },
    ],
});
