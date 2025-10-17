/* Copyright 2024 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html) */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("test_assortment_with_no_restriction", {
    url: "/shop",
    test: true,
    steps: () => [
        {
            trigger: "a:contains('Test Product 1')",
            run: "click",
        },
        {
            trigger: "a#add_to_cart",
            run: "click",
        },
        {
            trigger: "sup.my_cart_quantity:contains('1')",
        },
        {
            trigger: "a[href='/shop/cart']",
            run: "click",
        },
        {
            trigger: "input.js_quantity[value='1']",
        },
        {
            trigger: "a:contains('Test Product 1')",
        },
    ],
});
