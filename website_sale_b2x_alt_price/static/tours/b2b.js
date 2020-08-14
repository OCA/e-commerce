/* Copyright 2020 Jairo Llopis - Tecnativa
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

odoo.define("website_sale_b2x_alt_price.tour_b2b", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var searchResultsPage = "/shop?search=website_sale_b2x_alt_price";

    /**
     * Go directly to the filtered products page.
     *
     * Going to the main products page can produce some false positives if
     * there are demo products, and is slower because it means more steps and
     * downloading many product images, so we direct the tour directly via JS.
     */
    function goSearch() {
        window.location = searchResultsPage;
    }

    /**
     * Test eCommerce in B2B mode.
     *
     * Remember fields meaning:
     *
     * - .oe_currency_value: main price, without taxes.
     * - .text-danger: main price before discounts, without taxes.
     * - .js_alt_price: alt price, with taxes.
     * - .js_alt_list_price: alt price before discounts, with taxes.
     */
    tour.register(
        "website_sale_b2x_alt_price_b2b",
        {
            test: true,
            url: searchResultsPage,
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
                run: goSearch,
            },
            // Pen costs $5 + 22% tax
            {
                content: "select pen",
                trigger:
                    ".oe_product_cart:has(.js_alt_price :containsExact(6.10)):has(.oe_currency_value:containsExact(5.00)) a:contains('Pen')",
            },
            {
                content: "go back to search results",
                trigger:
                    "#product_details:has(.js_alt_price :containsExact(6.10)):has(.oe_currency_value:containsExact(5.00)):contains('Pen')",
                run: goSearch,
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
                    ".oe_product_cart:has(.js_alt_list_price:visible :containsExact(6.10)):has(.js_alt_price :containsExact(5.49)):has(.text-danger :containsExact(5.00)):has(.oe_currency_value:containsExact(4.50)) a:contains('Pen')",
            },
            {
                content: "go back to search results",
                trigger:
                    "#product_details:has(.js_alt_list_price:visible :containsExact(6.10)):has(.js_alt_price :containsExact(5.49)):has(.text-danger :containsExact(5.00)):has(.oe_currency_value:containsExact(4.50)):contains('Pen')",
                run: goSearch,
            },
            // A5 Notebook costs $3 - 10% discount + 22% tax
            {
                content: "select notebook",
                trigger:
                    ".oe_product_cart:has(.js_alt_list_price:visible :containsExact(3.66)):has(.js_alt_price :containsExact(3.29)):has(.text-danger :containsExact(3.00)):has(.oe_currency_value:containsExact(2.70)) a:contains('Notebook')",
            },
            // A4 Notebook costs $3.50 - 10% discount + 22% tax
            {
                content: "select variant: a4 size",
                extra_trigger:
                    "#product_details:has(.js_alt_list_price:visible :containsExact(3.66)):has(.js_alt_price :containsExact(3.29)):has(.text-danger :containsExact(3.00)):has(.oe_currency_value:containsExact(2.70)):contains('Notebook')",
                trigger: ".js_attribute_value:contains('A4') :radio",
            },
            {
                content: "open pricelist selector",
                extra_trigger:
                    "#product_details:has(.js_alt_list_price:visible :containsExact(4.27)):has(.js_alt_price :containsExact(3.84)):has(.text-danger :containsExact(3.50)):has(.oe_currency_value:containsExact(3.15)):contains('Notebook')",
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
                    "#product_details:not(:has(.js_alt_list_price:visible, .text-danger:visible)):has(.js_alt_price :containsExact(3.66)):has(.oe_currency_value:containsExact(3.00)):contains('Notebook')",
                trigger: ".js_attribute_value:contains('A4') :radio",
            },
            {
                content: "select variant: a5 size",
                extra_trigger:
                    "#product_details:not(:has(.js_alt_list_price:visible, .text-danger:visible)):has(.js_alt_price :containsExact(4.27)):has(.oe_currency_value:containsExact(3.50)):contains('Notebook')",
                trigger: ".js_attribute_value:contains('A5') :radio",
            },
            {
                content: "check a5 price is fine",
                trigger:
                    "#product_details:not(:has(.js_alt_list_price:visible, .text-danger:visible)):has(.js_alt_price :containsExact(3.66)):has(.oe_currency_value:containsExact(3.00)):contains('Notebook')",
            },
        ]
    );

    return {
        searchResultsPage: searchResultsPage,
        goSearch: goSearch,
    };
});
