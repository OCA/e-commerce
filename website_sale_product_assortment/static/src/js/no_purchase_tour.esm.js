/* Copyright 2024 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html) */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("test_assortment_with_no_purchase", {
    url: "/shop",
    steps: () => [
        {
            trigger:
                ".oe_product_cart:has(.text-danger:has(.fa-exclamation-triangle)) a:contains('Test Product 1')",
            run: "click",
        },
        {
            trigger: ".text-danger:has(.fa-exclamation-triangle)",
        },
        {
            trigger: "a#add_to_cart.disabled",
            run: "click",
        },
        {
            trigger: "span[name='testing']",
        },
        {
            trigger: "a[href='/shop']",
            run: "click",
        },
    ],
});
