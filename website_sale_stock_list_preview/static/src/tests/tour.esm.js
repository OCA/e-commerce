/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_stock_list_preview", {
    url: "/shop",
    steps: () => [
        {
            trigger:
                ".o_wsale_product_information:has(.text-warning:contains('Only 30 Units left in stock.')) a:contains('Test Product 1')",
            run: "click",
            expectUnloadPage: true,
        },
        {
            // Verify product page loaded natively without tying to brittle native stock strings
            trigger: "#product_details",
        },
        {
            trigger: "a[href='/shop']",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger:
                ".o_wsale_product_information:has(.text-warning:contains('Only 5 Units left in stock.')) a:contains('Test Product 3')",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "#product_details",
        },
        {
            trigger: "a[href='/shop']",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger:
                ".o_wsale_product_information:contains('test message') a:contains('Test Product 4')",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "#product_details",
        },
        {
            trigger: "a[href='/shop']",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger:
                ".o_wsale_product_information:contains('Out of Stock') a:contains('Test Product 6')",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "#product_details",
        },
        {
            trigger: "a[href='/shop']",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger:
                ".o_wsale_product_information:contains('Out of Stock') a:contains('Test Product 7')",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "#product_details",
        },
    ],
});
