/** @odoo-module **/

import {registry} from "@web/core/registry";
// Import {stepUtils} from "@web_tour/tour_service/tour_utils";

const searchResultsPage = "/shop?search=website_sale_b2x_alt_price";

// Function goSearch() {
//     window.location = searchResultsPage;
// }

const goSearch = function () {
    window.location = searchResultsPage;
};

registry.category("web_tour.tours").add("website_sale_b2x_alt_price_b2b", {
    url: searchResultsPage,
    test: true,
    steps: () => [
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
            trigger:
                ".switcher_pricelist:containsExact('website_sale_b2x_alt_price discounted')",
        },
        // Pen now has 10% discount
        // {
        //     content: "select pen",
        //     trigger:
        //         ".oe_product_cart:has(.js_alt_list_price:visible :containsExact(6.10)):has(.js_alt_price :containsExact(5.49)):has(.text-danger :containsExact(5.00)):has(.oe_currency_value:containsExact(4.50)) a:contains('Pen')",
        // },
        // {
        //     content: "go back to search results",
        //     trigger:
        //         "#product_details:has(.js_alt_list_price:visible :containsExact(6.10)):has(.js_alt_price :containsExact(5.49)):has(.text-danger :containsExact(5.00)):has(.oe_currency_value:containsExact(4.50)):contains('Pen')",
        //     run: goSearch,
        // },
        // // A5 Notebook costs $3 - 10% discount + 22% tax
        // {
        //     content: "select notebook",
        //     trigger:
        //         ".oe_product_cart:has(.js_alt_list_price:visible :containsExact(3.66)):has(.js_alt_price :containsExact(3.29)):has(.text-danger :containsExact(3.00)):has(.oe_currency_value:containsExact(2.70)) a:contains('Notebook')",
        // },
        // // A4 Notebook costs $3.50 - 10% discount + 22% tax
        // {
        //     content: "select variant: a4 size",
        //     extra_trigger:
        //         "#product_details:has(.js_alt_list_price:visible :containsExact(3.66)):has(.js_alt_price :containsExact(3.29)):has(.text-danger :containsExact(3.00)):has(.oe_currency_value:containsExact(2.70)):contains('Notebook')",
        //     trigger: ".js_attribute_value:contains('A4') :radio",
        // },
        // {
        //     content: "open pricelist selector",
        //     extra_trigger:
        //         "#product_details:has(.js_alt_list_price:visible :containsExact(4.27)):has(.js_alt_price :containsExact(3.84)):has(.text-danger :containsExact(3.50)):has(.oe_currency_value:containsExact(3.15)):contains('Notebook')",
        //     trigger: ".btn:containsExact('website_sale_b2x_alt_price discounted')",
        // },
        // // Change to "website_sale_b2x_alt_price public" pricelist; 10% discount disappears
        // {
        //     content: "select website_sale_b2x_alt_price public",
        //     trigger:
        //         ".switcher_pricelist:containsExact('website_sale_b2x_alt_price public')",
        // },
        // {
        //     content: "select variant: a4 size",
        //     // When changing pricelist, product was reset to Notebook A5
        //     extra_trigger:
        //         "#product_details:not(:has(.js_alt_list_price:visible, .text-danger:visible)):has(.js_alt_price :containsExact(3.66)):has(.oe_currency_value:containsExact(3.00)):contains('Notebook')",
        //     trigger: ".js_attribute_value:contains('A4') :radio",
        // },
        // {
        //     content: "select variant: a5 size",
        //     extra_trigger:
        //         "#product_details:not(:has(.js_alt_list_price:visible, .text-danger:visible)):has(.js_alt_price :containsExact(4.27)):has(.oe_currency_value:containsExact(3.50)):contains('Notebook')",
        //     trigger: ".js_attribute_value:contains('A5') :radio",
        // },
        // {
        //     content: "check a5 price is fine",
        //     trigger:
        //         "#product_details:not(:has(.js_alt_list_price:visible, .text-danger:visible)):has(.js_alt_price :containsExact(3.66)):has(.oe_currency_value:containsExact(3.00)):contains('Notebook')",
        // },
    ],
});
