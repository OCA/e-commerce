/* Copyright 2020 Tecnativa - João Marques
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_order_type_tour", {
    test: true,
    url: "/shop",
    steps: () => [
        {
            trigger: ".oe_product_cart a:contains('Test Product SO Type')",
        },
        {
            trigger: "#add_to_cart",
        },
        {
            trigger: "a[href='/shop/cart']",
            extra_trigger: "sup.my_cart_quantity:contains('1')",
        },
        {
            trigger: ".btn:contains('Process Checkout')",
        },
    ],
});
