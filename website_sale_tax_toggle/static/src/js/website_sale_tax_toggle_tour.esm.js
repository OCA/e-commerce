/** @odoo-module **/
/* Copyright 2020 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import tour from "web_tour.tour";

// Notice that it's important targeting the price as `span .oe_currency_value`
// or `.oe_price .oe_currency_value` to make sure this test is compatible
// with website_sale_b2x_alt_price module in this same repo.
const steps = [
    {
        content: "Toggle tax button click from list page",
        trigger: ".js_tax_toggle_btn",
        extra_trigger:
            ".oe_product_cart:contains('Product test tax toggle') span .oe_currency_value:containsExact('750.00')",
    },
    {
        content: "Enter the product page",
        trigger:
            ".oe_product_cart:has(span .oe_currency_value:containsExact('862.50')) a:contains('Product test tax toggle')",
        extra_trigger: ".o_switch_danger:has(input:checked)",
    },
    {
        content: "Toggle tax button click from product page",
        trigger: ".js_tax_toggle_btn",
        extra_trigger:
            "#product_details .oe_price .oe_currency_value:containsExact('862.50')",
    },
    {
        content: "Check the product price is back to what it should",
        trigger:
            "#product_details .oe_price .oe_currency_value:containsExact('750.00')",
        extra_trigger: ".o_switch_danger:has(input:not(:checked))",
    },
];
tour.register(
    "website_sale_tax_toggle",
    {
        url: "/shop",
        test: true,
    },
    steps
);
