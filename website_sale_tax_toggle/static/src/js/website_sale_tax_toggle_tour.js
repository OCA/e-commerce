/* Copyright 2020 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_tax_toggle.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: "a:contains('Customizable Desk')",
            extra_trigger: ".product_price:has(span:contains('750.00'))",
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            content: "Toggle tax button click",
            trigger: '.js_tax_toggle_btn',
            run: function() {
                    $('.js_tax_toggle_btn').trigger('click');
            },
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: "a:contains('Customizable Desk')",
            extra_trigger: ".product_price:has(span:contains('862.50'))",
        },
        {
            content: "Toggle tax button click",
            trigger: '.js_tax_toggle_btn',
            run: function() {
                    $('.js_tax_toggle_btn').trigger('click');
            },
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: "a:contains('Customizable Desk')",
            extra_trigger: ".product_price:has(span:contains('750.00'))",
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
