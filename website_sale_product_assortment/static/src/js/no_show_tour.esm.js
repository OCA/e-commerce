/* Copyright 2024 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html) */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("test_assortment_with_no_show", {
    url: "/shop",
    steps: () => [
        {
            trigger:
                ".o_wsale_product_grid_wrapper:not(:has(a:contains('Test Product 1')))",
        },
        {
            trigger: "a[href='/shop']",
            run: "click",
        },
    ],
});
