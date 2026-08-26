/* Copyright 2024 Pilar Vargas
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_menu_partner_top_selling", {
    url: "/shop",
    steps: () => [
        {
            trigger: "#products_grid_before a:contains('My Regular Products')",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger:
                "#products_grid:has(a:contains('Product 5')):has(a:contains('Product 3')):not(:has(a:contains('Product 1'))):not(:has(a:contains('Product 2'))):not(:has(a:contains('Product 4')))",
        },
    ],
});
