/* Copyright 2020 Sergio Teruel
   Copyright 2026 Tecnativa - Adasat Torres
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
import {browser} from "@web/core/browser/browser";

registry.category("web_tour.tours").add("website_sale_tax_toggle", {
    url: "/shop?search=Product+test+tax+toggle",
    steps: () => [
        {
            content: "Prices exclude taxes by default",
            trigger: ".js_tax_toggle_btn input:not(:checked)",
        },
        {
            trigger: "span.oe_currency_value:contains('750.00')",
        },
        {
            content: "Toggle tax button click from list page",
            trigger: ".js_tax_toggle_btn input",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "span.oe_currency_value:contains('862.50')",
        },
        {
            content: "Enter the product page",
            trigger: '.oe_product_cart a:contains("Product test tax toggle")',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "The toggle switch remains active.",
            trigger: ".js_tax_toggle_btn:has(input:checked)",
        },
        {
            content: "The price is shown including taxes.",
            trigger: "span.oe_currency_value:contains('862.50')",
        },
        {
            content: "Toggle tax button click from product page",
            trigger: ".js_tax_toggle_btn input",
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Check the product price is back to what it should",
            trigger: "span.oe_currency_value:contains('750.00')",
        },
        {
            content: "Reload with taxes excluded",
            trigger: ".js_tax_toggle_btn input:not(:checked)",
            expectUnloadPage: true,
            run() {
                browser.location.reload();
            },
        },
        {
            content: "The switch stays off after reloading",
            trigger: ".js_tax_toggle_btn input:not(:checked)",
        },
        {
            content: "The price still excludes taxes after reloading",
            trigger: "span.oe_currency_value:contains('750.00')",
        },
    ],
});
