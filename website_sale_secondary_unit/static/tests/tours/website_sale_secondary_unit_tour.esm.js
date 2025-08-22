/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
registry.category("web_tour.tours").add("website_sale_secondary_unit", {
    test: true,
    url: "/shop",
    steps: () => [
        {
            trigger: "a:contains('Test product')",
            run: "click",
        },
        {
            trigger: "#secondary_uom",
            run: "selectByLabel Box 5 Units",
        },
        {
            trigger: "#add_to_cart",
            run: "click",
        },
        {
            trigger: "a[href='/shop/cart']",
            run: "click",
        },
        {
            trigger: "span:contains(Box 5 Units)",
        },
        {
            trigger: "a[href='/shop']",
            run: "click",
        },
        {
            trigger: "a:contains('Test product')",
            run: "click",
        },
        {
            trigger: "#add_to_cart",
            run: "click",
        },
        {
            trigger: "a[href='/shop/cart']",
            run: "click",
        },
        {
            trigger: "span:contains(Units)",
        },
        {
            trigger: "a[name='website_sale_main_button']",
            run: "click",
        },
        {
            trigger: "div[id='o_wsale_total_accordion_item'] button.accordion-button",
            run: "click",
        },
        {
            trigger: "h6[name='secondary_uom_qty'] span:contains(Box 5)",
            run: "click",
        },
        {
            trigger: "table:has(span:contains(Box 5)):has(span:contains(Units))",
        },
        {
            trigger: "a[href='/shop']",
            run: "click",
        },
    ],
});
