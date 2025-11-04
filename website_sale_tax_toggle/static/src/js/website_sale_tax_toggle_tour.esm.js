/* Copyright 2020 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_tax_toggle", {
    url: "/shop?search=Product+test+tax+toggle",
    steps: () => [
        {
            trigger: "span.oe_currency_value:contains('750.00')",
        },
        {
            content: "Toggle tax button click from list page",
            trigger: ".js_tax_toggle_btn",
            run: "click",
        },
        {
            trigger: "span.oe_currency_value:contains('862.50')",
        },
        {
            content: "Enter the product page",
            trigger: '.oe_product_cart a:contains("Product test tax toggle")',
            run: "click",
        },
        {
            content: "The toggle switch remains active.",
            trigger: ".o_switch_danger:has(input:checked)",
        },
        {
            content: "The price is shown including taxes.",
            trigger: "span.oe_currency_value:contains('862.50')",
        },
        {
            content: "Toggle tax button click from product page",
            trigger: ".js_tax_toggle_btn",
            run: "click",
        },
        {
            content: "Check the product price is back to what it should",
            trigger: "span.oe_currency_value:contains('750.00')",
        },
    ],
});
