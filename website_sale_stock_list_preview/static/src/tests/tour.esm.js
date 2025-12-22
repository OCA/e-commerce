/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_stock_list_preview", {
    url: "/shop",
    steps: () => [
        {
            trigger:
                ".o_wsale_product_information:has(.text-warning:contains('Only 30 Units left in stock.')) a:contains('Test Product 1')",
            run: "click",
        },
        {
            trigger:
                ".o_wsale_product_information:contains('Only 30 Units left in stock.')",
        },
        {
            trigger: "a[href='/shop']",
            run: "click",
        },
        {
            trigger:
                ".o_wsale_product_information:has(.text-warning:contains('Only 5 Units left in stock.')) a:contains('Test Product 3')",
            run: "click",
        },
        {
            trigger:
                ".o_wsale_product_information:contains('Only 5 Units left in stock.')",
        },
        {
            trigger: "a[href='/shop']",
            run: "click",
        },
        {
            trigger:
                ".o_wsale_product_information:contains('test') a:contains('Test Product 4')",
            run: "click",
        },
        {
            trigger: "#product_details #out_of_stock_message:contains('test message')",
        },
        {
            trigger: "a[href='/shop']",
            run: "click",
        },
        {
            trigger: "div:contains('Out of Stock') a:contains('Test Product 6')",
            run: "click",
        },
        {
            trigger: "#out_of_stock_message:contains('Out of Stock')",
        },
        {
            trigger: "a[href='/shop']",
            run: "click",
        },
        {
            trigger: "div:contains('Out of Stock') a:contains('Test Product 7')",
            run: "click",
        },
        {
            trigger: "#out_of_stock_message:contains('Out of Stock')",
        },
    ],
});
