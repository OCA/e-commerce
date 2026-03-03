/* Copyright 2020 Tecnativa - João Marques
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_order_type_tour", {
    test: true,
    url: "/shop?search=Test Product SO Type",
    steps: () => [
        {
            trigger: ".oe_product_cart a:text(Test Product SO Type)",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "#add_to_cart",
            run: "click",
        },
        {
            trigger: "sup.my_cart_quantity:contains('1')",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: ".btn:contains('Checkout')",
        },
    ],
});
