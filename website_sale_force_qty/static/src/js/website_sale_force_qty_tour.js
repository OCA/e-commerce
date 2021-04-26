/* Copyright 2021 Tecnativa - João Marques
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

 odoo.define("website_sale_force_qty.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a:contains('Test product with fixed quantity')",
        },
        {
            extra_trigger: [
                "div.js_main_product",
                // The quantity input box is disable and is set to 2
                ":has(input[name=add_qty][value='2']:disabled)",
                // There is a badge indicating the product as a fixed quantity
                ":has(.text-info:contains('This product has a fixed quantity'))",
            ].join(""),
            trigger: "a:contains('Add to Cart')",
        },
        {
            extra_trigger: [
                "div.oe_website_sale",
                // Product 1 has the same badge and the quantity is still set to 2 and blocked
                ":has(tr:contains('Test product with fixed quantity') .badge:contains('This product has a fixed quantity'))",
                ":has(tr:contains('Test product with fixed quantity') .td-qty .js_quantity:propValue('2'):disabled)",
                // The subtotal value os 2 (2 units * 1$)
                ":has(#order_total_untaxed .oe_currency_value:contains('2.00'))",
            ].join(""),
            trigger: "a[href='/shop']",
        },
        {
            trigger: "a:contains('Test product with variants, optionals and fixed quantity')",
        },
        {
            extra_trigger: [
                "div.js_main_product",
                // The quantity input box is disable and is set to 2
                ":has(input[name=add_qty][value='3']:disabled)",
                // There is a badge indicating the product as a fixed quantity
                ":has(.text-info:contains('This product has a fixed quantity'))",
            ].join(""),
            trigger: "a:contains('Add to Cart')",
        },
        {
            // The optional products modal opens
            extra_trigger: [
                ".oe_optional_products_modal",
                // Product has the same badge and the quantity is still set to 3 and blocked
                ":has(tr.main_product:contains('Test product with variants, optionals and fixed quantity') .badge:contains('This product has a fixed quantity'))",
                ":has(tr.main_product:contains('Test product with variants, optionals and fixed quantity') .td-qty .js_quantity:propValue('3'):disabled)",
                // The subtotal value os 3 (3 units * 1$)
                ":has(.js_price_total .oe_currency_value:containsExact('3.00'))",
            ].join(""),
            trigger: ".btn-primary:contains('Proceed to Checkout')",
        },
        {
            // In cart
            extra_trigger: [
                "div.oe_website_sale",
                // Product 1 has the same badge and the quantity is still set to 2 and blocked
                ":has(tr:contains('Test product with variants, optionals and fixed quantity') .badge:contains('This product has a fixed quantity'))",
                ":has(tr:contains('Test product with variants, optionals and fixed quantity') .td-qty .js_quantity:propValue('3'):disabled)",
                // The subtotal value os 5 (3 units * 1$ + 2 prev. product units * 1$)
                ":has(#order_total_untaxed .oe_currency_value:contains('5.00'))",
            ].join(""),
            trigger: "a[href='/shop']",
        },
        {
            trigger: "a:contains('Test product normal')",
        },
        {
            // The quantity input box should be editable and the buttons should work
            trigger: "a.js_add_cart_json[title='Add one']",
        },
        {
            extra_trigger: [
                "div.js_main_product",
                // Shouldn't be disabled
                ":not(:has(input[name=add_qty]:disabled))",
                // There shouldn't be a flag indicating the fixed quantity
                ":not(:has(.text-info:contains('This product has a fixed quantity')))",
            ].join(""),
            trigger: "a:contains('Add to Cart')",
        },
        {
            // In cart
            extra_trigger: [
                "div.oe_website_sale",
                // Product has no badge, the quantity is set to 2 but not blocked
                ":has(tr:contains('Test product normal') :not(:has(.badge:contains('This product has a fixed quantity'))))",
                ":has(tr:contains('Test product normal') .td-qty .js_quantity:propValue('2'))",
                ":has(tr:contains('Test product normal') .td-qty :not(:has(.js_quantity:disabled)))",
            ].join(""),
            // The quantity input box should be editable and the buttons should work
            trigger: "a.js_add_cart_json[title='Add one']",
        },
        {
            extra_trigger: [
                "div.oe_website_sale",
                // Product has no badge, the quantity is set to 3 but not blocked
                ":has(tr:contains('Test product normal') :not(:has(.badge:contains('This product has a fixed quantity'))))",
                ":has(tr:contains('Test product normal') .td-qty .js_quantity:propValue('3'))",
                ":has(tr:contains('Test product normal') .td-qty :not(:has(.js_quantity:disabled)))",
                // The subtotal value os 8 (3 * 1$ + 3 prev. product units * 1$ + 2 prev. product units * 1$)
                ":has(#order_total_untaxed .oe_currency_value:contains('8.00'))",
            ].join(""),
            trigger: ".btn-primary:contains('Process Checkout')",
        },
    ];

    tour.register("website_sale_force_qty",
        {
            url: "/shop",
            test: true,
            wait_for: base.ready(),
        },
        steps
    );

});
