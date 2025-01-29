/* Copyright 2020 Jairo Llopis - Tecnativa
 * Copyright 2024 Carlos Lopez - Tecnativa
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {registry} from "@web/core/registry";

const searchResultsPage = "/shop?search=website_sale_b2x_alt_price";

/**
 * Go directly to the filtered products page.
 *
 * Going to the main products page can produce some false positives if
 * there are demo products, and is slower because it means more steps and
 * downloading many product images, so we direct the tour directly via JS.
 */
function goSearch() {
    // eslint-disable-next-line no-undef
    window.location = searchResultsPage;
}

/**
 * Test eCommerce in B2B mode.
 *
 * Remember fields meaning:
 *
 * - .oe_currency_value: main price, without taxes.
 * - .text-muted.me-1.h6.mb-0: main price before discounts, without taxes(on products list).
 * - .text-muted: main price before discounts, without taxes(on product Item).
 * - .js_alt_price: alt price, with taxes.
 * - .js_alt_list_price: alt price before discounts, with taxes.
 */
registry.category("web_tour.tours").add("website_sale_b2x_alt_price_b2b", {
    url: searchResultsPage,
    steps: () => [
        // "Training on accounting" costs $100; no taxes, so no alt price
        {
            content: "select training on accounting product",
            trigger:
                ".oe_product_cart:not(:has(.js_alt_price)):has(.oe_currency_value:contains(/^100.00$/)) a:contains('Training on accounting')",
            run: "click",
        },
        {
            content: "go back to search results",
            trigger:
                "#product_details:not(:has(.js_alt_price)):has(.oe_currency_value:contains(/^100.00$/)):contains('Training on accounting')",
            run: goSearch,
        },
        // Pen costs $5 + 22% tax
        {
            content: "select pen",
            trigger:
                ".oe_product_cart:has(.js_alt_price :contains(/^6.10$/)):has(.oe_currency_value:contains(/^5.00$/)) a:contains('Pen')",
            run: "click",
        },
        {
            content: "go back to search results",
            trigger:
                "#product_details:has(.js_alt_price :contains(/^6.10$/)):has(.oe_currency_value:contains(/^5.00$/)):contains('Pen')",
            run: goSearch,
        },
        {
            content: "Check Pen price",
            trigger:
                ".oe_product_cart:not(:has(.js_alt_list_price:visible, .text-danger:visible)) a:contains('Pen')",
        },
        // Switch to "website_sale_b2x_alt_price discounted" pricelist
        {
            content: "open pricelist selector",
            trigger: ".btn:contains(/^website_sale_b2x_alt_price public$/)",
            run: "click",
        },
        {
            content: "select website_sale_b2x_alt_price discounted",
            trigger:
                ".switcher_pricelist:contains(/^website_sale_b2x_alt_price discounted$/)",
            run: "click",
        },
        // Pen now has 10% discount
        {
            content: "select pen",
            trigger:
                ".oe_product_cart:has(.js_alt_list_price:visible :contains(/^6.10$/)):has(.js_alt_price :contains(/^5.49$/)):has(.text-muted.me-1.h6.mb-0 :contains(/^5.00$/)):has(.oe_currency_value:contains(/^4.50$/)) a:contains('Pen')",
            run: "click",
        },
        {
            content: "go back to search results",
            trigger:
                "#product_details:has(.js_alt_list_price:visible :contains(/^6.10$/)):has(.js_alt_price :contains(/^5.49$/)):has(.text-muted :contains(/^5.00$/)):has(.oe_currency_value:contains(/^4.50$/)):contains('Pen')",
            run: goSearch,
        },
        // A5 Notebook costs $3 - 10% discount + 22% tax
        {
            content: "select notebook",
            trigger:
                ".oe_product_cart:has(.js_alt_list_price:visible :contains(/^3.66$/)):has(.js_alt_price :contains(/^3.29$/)):has(.text-muted.me-1.h6.mb-0 :contains(/^3.00$/)):has(.oe_currency_value:contains(/^2.70$/)) a:contains('Notebook')",
            run: "click",
        },
        {
            content: "Check Notebook price a5",
            trigger:
                "#product_details:has(.js_alt_list_price:visible :contains(/^3.66$/)):has(.js_alt_price :contains(/^3.29$/)):has(.text-muted :contains(/^3.00$/)):has(.oe_currency_value:contains(/^2.70$/)):contains('Notebook')",
        },
        // A4 Notebook costs $3.50 - 10% discount + 22% tax
        {
            content: "select variant: a4 size",
            trigger: ".js_attribute_value span:contains('A4')",
            run: "click",
        },
        {
            content: "check a4 price is fine",
            trigger:
                "#product_details:has(.js_alt_list_price:visible :contains(/^4.27$/)):has(.js_alt_price :contains(/^3.84$/)):has(.text-muted :contains(/^3.50$/)):has(.oe_currency_value:contains(/^3.15$/)):contains('Notebook')",
            run: "click",
        },
        // Change to "website_sale_b2x_alt_price public" pricelist; 10% discount disappears
        {
            content: "open pricelist selector",
            trigger: ".btn:contains(/^website_sale_b2x_alt_price discounted$/)",
            run: "click",
        },
        {
            content: "select website_sale_b2x_alt_price public",
            trigger:
                ".switcher_pricelist:contains(/^website_sale_b2x_alt_price public$/)",
            run: "click",
        },
        // When changing pricelist, product was reset to Notebook A5
        {
            content: "check a5 price is fine",
            trigger:
                "#product_details:not(:has(.js_alt_list_price:visible, .text-danger:visible)):has(.js_alt_price :contains(/^3.66$/)):has(.oe_currency_value:contains(/^3.00$/)):contains('Notebook')",
            run: "click",
        },
        // Change to a4 size
        {
            content: "select variant: a4 size",
            trigger: ".js_attribute_value span:contains('A4')",
            run: "click",
        },
        {
            content: "check a4 price is fine",
            trigger:
                "#product_details:not(:has(.js_alt_list_price:visible, .text-danger:visible)):has(.js_alt_price :contains(/^4.27$/)):has(.oe_currency_value:contains(/^3.50$/)):contains('Notebook')",
            run: "click",
        },
        {
            content: "select variant: a5 size",
            trigger: ".js_attribute_value span:contains('A5')",
            run: "click",
        },
        {
            content: "check a5 price is fine",
            trigger:
                "#product_details:not(:has(.js_alt_list_price:visible, .text-danger:visible)):has(.js_alt_price :contains(/^3.66$/)):has(.oe_currency_value:contains(/^3.00$/)):contains('Notebook')",
        },
    ],
});

export default {
    searchResultsPage: searchResultsPage,
    goSearch: goSearch,
};
