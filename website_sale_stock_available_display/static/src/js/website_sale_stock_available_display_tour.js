/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_stock_available_display.tour", function(require) {
    "use strict";

    const tour = require("web_tour.tour");
    const base = require("web_editor.base");

    const steps = [
        {
            trigger: "a:contains('Computer Motherboard')",
        },
        {
            trigger: "a#add_to_cart",
            extra_trigger:
                ".availability_messages:has(div.text-danger):has(div:contains('Available in 10 days'))",
        },
        {
            trigger: "span:contains('Process Checkout')",
            extra_trigger:
                ".availability_messages:has(span:contains('0 Units in stock'))",
        },
        {
            trigger: ".btn-primary:contains('Confirm Order')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger:
                ".availability_messages:has(span:contains('0 Units in stock'))",
        },
        {
            trigger: "a:contains('Special Mouse')",
        },
        {
            trigger: "a#add_to_cart",
            extra_trigger: ".availability_messages:has(div.text-success)",
        },
        {
            trigger: "span:contains('Process Checkout')",
            extra_trigger:
                ".availability_messages:has(span:contains('10.0 Units in stock'))",
        },
        {
            trigger: ".btn-primary:contains('Confirm Order')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger:
                ".availability_messages:has(span:contains('10.0 Units in stock'))",
        },
    ];
    tour.register(
        "website_sale_stock_available_display",
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
