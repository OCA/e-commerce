/* Copyright 2020 Jairo Llopis - Tecnativa
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

odoo.define("website_sale_b2x_alt_price.tour_b2c", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");
    var tour_b2b = require("website_sale_b2x_alt_price.tour_b2b");

    /**
     * Test eCommerce in B2C mode.
     *
     * Remember fields meaning:
     *
     * - .oe_currency_value: main price, with taxes.
     * - .text-danger: main price before discounts, with taxes.
     * - .js_alt_price: alt price, without taxes.
     * - .js_alt_list_price: alt price before discounts, without taxes.
     */
    tour.register(
        "website_sale_b2x_alt_price_b2c",
        {
            test: true,
            url: tour_b2b.searchResultsPage,
            wait_for: base.ready(),
        },
        [
            // "Training on accounting" costs $100; no taxes, so no alt price
            {
                content: "select training on accounting product",
                trigger:
                    ".oe_product_cart:not(:has(.js_alt_price)):has(.oe_currency_value:containsExact(100.00)) a:contains('Training on accounting')",
            },
            {
                content: "go back to search results",
                trigger:
                    "#product_details:not(:has(.js_alt_price)):has(.oe_currency_value:containsExact(100.00)):contains('Training on accounting')",
                run: tour_b2b.goSearch,
            },
            // Pen costs $5 + 22% tax
            {
                content: "select pen",
                trigger:
                    ".oe_product_cart:has(.js_alt_price :containsExact(5.00)):has(.oe_currency_value:containsExact(6.10)) a:contains('Pen')",
            },
            {
                content: "go back to search results",
                trigger:
                    "#product_details:has(.js_alt_price :containsExact(5.00)):has(.oe_currency_value:containsExact(6.10)):contains('Pen')",
                run: tour_b2b.goSearch,
            },
            // Switch to "website_sale_b2x_alt_price discounted" pricelist
            {
                content: "open pricelist selector",
                extra_trigger:
                    ".oe_product_cart:not(:has(.js_alt_list_price:visible, .text-danger:visible)) a:contains('Pen')",
                trigger: ".btn:containsExact('website_sale_b2x_alt_price public')",
            },
            {
                content: "select website_sale_b2x_alt_price discounted",
                trigger: ".switcher_pricelist:containsExact('website_sale_b2x_alt_price discounted')",
            },
            // Pen now has 10% discount
            {
                content: "select pen",
                trigger:
                    ".oe_product_cart:has(.js_alt_list_price:visible :containsExact(5.00)):has(.js_alt_price :containsExact(4.50)):has(.text-danger :containsExact(6.10)):has(.oe_currency_value:containsExact(5.49)) a:contains('Pen')",
            },
            {
                content: "go back to search results",
                trigger:
                    "#product_details:has(.js_alt_list_price:visible :containsExact(5.00)):has(.js_alt_price :containsExact(4.50)):has(.text-danger :containsExact(6.10)):has(.oe_currency_value:containsExact(5.49)):contains('Pen')",
                run: tour_b2b.goSearch,
            },
            // A5 Notebook costs $3 - 10% discount + 22% tax
            {
                content: "select notebook",
                trigger:
                    ".oe_product_cart:has(.js_alt_list_price:visible :containsExact(3.00)):has(.js_alt_price :containsExact(2.70)):has(.text-danger :containsExact(3.66)):has(.oe_currency_value:containsExact(3.29)) a:contains('Notebook')",
            },
            // A4 Notebook costs $3.50 - 10% discount + 22% tax
            {
                content: "select variant: a4 size",
                extra_trigger:
                    "#product_details:has(.js_alt_list_price:visible :containsExact(3.00)):has(.js_alt_price :containsExact(2.70)):has(.text-danger :containsExact(3.66)):has(.oe_currency_value:containsExact(3.29)):contains('Notebook')",
                trigger: ".js_attribute_value:contains('A4') :radio",
            },
            {
                content: "open pricelist selector",
                extra_trigger:
                    "#product_details:has(.js_alt_list_price:visible :containsExact(3.50)):has(.js_alt_price :containsExact(3.15)):has(.text-danger :containsExact(4.27)):has(.oe_currency_value:containsExact(3.15)):contains('Notebook')",
                trigger: ".btn:containsExact('website_sale_b2x_alt_price discounted')",
            },
            // Change to "website_sale_b2x_alt_price public" pricelist; 10% discount disappears
            {
                content: "select website_sale_b2x_alt_price public",
                trigger: ".switcher_pricelist:containsExact('website_sale_b2x_alt_price public')",
            },
            {
                content: "select variant: a4 size",
                // When changing pricelist, product was reset to Notebook A5
                extra_trigger:
                    "#product_details:not(:has(.js_alt_list_price:visible, .text-danger:visible)):has(.js_alt_price :containsExact(3.00)):has(.oe_currency_value:containsExact(3.66)):contains('Notebook')",
                trigger: ".js_attribute_value:contains('A4') :radio",
            },
            {
                content: "select variant: a5 size",
                extra_trigger:
                    "#product_details:not(:has(.js_alt_list_price:visible, .text-danger:visible)):has(.js_alt_price :containsExact(3.50)):has(.oe_currency_value:containsExact(4.27)):contains('Notebook')",
                trigger: ".js_attribute_value:contains('A5') :radio",
            },
            {
                content: "check a5 price is fine",
                trigger:
                    "#product_details:not(:has(.js_alt_list_price:visible, .text-danger:visible)):has(.js_alt_price :containsExact(3.00)):has(.oe_currency_value:containsExact(3.66)):contains('Notebook')",
            },
        ]
    );
});
