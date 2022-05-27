/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_secondary_unit.tour", function (require) {
    "use strict";

    const tour = require("web_tour.tour");
    const base = require("web_editor.base");

    const steps = [
        {
            trigger: "a:contains('Test product')",
        },
        {
            trigger: "#secondary_uom",
            run: "text(Box 5 Units)",
        },
        {
            trigger: "#add_to_cart",
            extra_trigger:
                ".js_product:has(input[name='add_qty']:propValueContains(5)):has(.price_uom)",
        },
        {
            trigger: "a[href='/shop/cart']",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "span:contains(Box 5 Units)",
        },
        {
            trigger: "a:contains('Test product')",
        },
        {
            trigger: "#add_to_cart",
            extra_trigger:
                ".js_product:has(input[name='add_qty']:propValueContains(1))",
        },
        {
            trigger: "a[href='/shop/cart']",
        },
        {
            trigger: "a[href='/shop/checkout?express=1']",
            extra_trigger: "span:containsExact(Units)",
        },
        {
            trigger: "button[name='o_payment_submit_button']",
            extra_trigger:
                "table:has(span:contains(Box 5 Units)):has(span:contains(Units))",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger:
                "table:has(span:contains(Box 5 Units)):has(span:contains(Units))",
        },
    ];

    tour.register(
        "website_sale_secondary_unit",
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
