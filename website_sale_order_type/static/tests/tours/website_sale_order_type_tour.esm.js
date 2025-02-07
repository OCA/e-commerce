/** @odoo-module */
/* Copyright 2020 Tecnativa - João Marques
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_order_type_tour", {
    test: true,
    url: "/shop",
    steps: () => [
        {
            trigger: ".oe_product_cart a:contains('Test Product SO Type')",
            run: "click",
        },
        {
            trigger: "#add_to_cart",
            run: "click",
        },
        {
            trigger: "a[href='/shop/cart']",
        },
        {
            trigger: "sup.my_cart_quantity:contains('1')",
            run: "click",
        },
        {
            trigger: ".btn:contains('Checkout')",
        },
    ],
});
