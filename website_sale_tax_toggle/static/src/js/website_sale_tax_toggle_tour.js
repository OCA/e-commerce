/* Copyright 2020 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_tax_toggle.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    // Notice that it's important targeting the price as `b .oe_currency_value`
    // or `.oe_price .oe_currency_value` to make sure this test is compatible
    // with website_sale_b2x_alt_price module in this same repo.
    var steps = [
        {
            content: "Toggle tax button click from list page",
            trigger: '.js_tax_toggle_btn',
            extra_trigger: ".oe_product_cart:contains('Product test tax toggle') b .oe_currency_value:containsExact('750.00')",
        },
        {
            content: "Enter the product page",
            trigger: ".oe_product_cart:has(b .oe_currency_value:containsExact('862.50')) a:contains('Product test tax toggle')",
        },
        {
            content: "Toggle tax button click from product page",
            trigger: '.js_tax_toggle_btn',
            extra_trigger: "#product_details .oe_price .oe_currency_value:containsExact('862.50')",
        },
        {
            content: "Check the product price is back to what it should",
            trigger: "#product_details .oe_price .oe_currency_value:containsExact('750.00')",
        },
    ];
    tour.register("website_sale_tax_toggle",
        {
            url: "/shop",
            test: true,
            wait_for: base.ready(),
        },
        steps
    );
    return {
        steps: steps,
    };
});
