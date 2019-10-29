/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_stock_available_display.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a:contains('Computer Motherboard')",
        },
        {
            trigger: "a#add_to_cart",
            extra_trigger: ".availability_messages:has(span:contains('0 Unit(s) in stock')):has(div:contains('Available in 10 days'))",
        },
        {
            trigger: "span:contains('Process Checkout')",
            extra_trigger: ".availability_messages:has(span:contains('0 Unit(s) in stock'))",
        },
        {
            trigger: ".btn-primary:contains('Confirm Order')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: ".availability_messages:has(span:contains('0 Unit(s) in stock'))",
        },
        {
            trigger: "a:contains('Special Mouse')",
        },
        {
            trigger: "a#add_to_cart",
            extra_trigger: ".availability_messages:has(span:contains('10 Unit(s) in stock'))",
        },
        {
            trigger: "span:contains('Process Checkout')",
            extra_trigger: ".availability_messages:has(span:contains('10.0 Unit(s) in stock'))",
        },
        {
            trigger: ".btn-primary:contains('Confirm Order')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: ".availability_messages:has(span:contains('10.0 Unit(s) in stock'))",
        },
    ];
    tour.register("website_sale_stock_available_display",
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
