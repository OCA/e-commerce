/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_stock_list_preview.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger:
                ".o_wsale_product_information:has(#threshold_message:contains('Only 30 Units left in stock.')) a:contains('Test Product 1')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger:
                "#product_details #threshold_message:contains('Only 30 Units left in stock.')",
        },
        {
            trigger:
                ".o_wsale_product_information:not(:has(.btn-primary.disabled)) a:contains('Test Product 1')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "#product_details a:not(#add_to_cart.disabled)",
        },
        {
            trigger:
                ".o_wsale_product_information:not(:has(.btn-primary.disabled)) a:contains('Test Product 2')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "#product_details a:not(#add_to_cart.disabled)",
        },
        {
            trigger:
                ".o_wsale_product_information:has(#threshold_message:contains('Only 5 Units left in stock.')) a:contains('Test Product 3')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger:
                "#product_details #threshold_message:contains('Only 5 Units left in stock.')",
        },
        {
            trigger:
                ".o_wsale_product_information:not(:has(.btn-primary.disabled)) a:contains('Test Product 3')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "#product_details a:not(#add_to_cart.disabled)",
        },
        {
            trigger:
                ".o_wsale_product_information:has(#out_of_stock_message:contains('test message')) a:contains('Test Product 4')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger:
                "#product_details #out_of_stock_message:contains('test message')",
        },
        {
            trigger:
                ".o_wsale_product_information:not(:has(.btn-primary.disabled)) a:contains('Test Product 4')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "#product_details a:not(#add_to_cart.disabled)",
        },
        {
            trigger:
                ".o_wsale_product_information:has(.product_price:not(:has(.mt16))) a:contains('Test Product 5')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "#product_details :not(.mt16)",
        },
        {
            trigger:
                ".o_wsale_product_information:not(:has(btn-primary.disabled)) a:contains('Test Product 5')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "#product_details a:not(#add_to_cart.disabled)",
        },
        {
            trigger:
                ".o_wsale_product_information:has(#out_of_stock_message:contains('Out of stock')) a:contains('Test Product 6')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger:
                "#product_details #out_of_stock_message:contains('Out of stock')",
        },
        {
            trigger:
                ".o_wsale_product_information:not(:has(.btn-primary.disabled)) a:contains('Test Product 6')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "#product_details :not(a#add_to_cart.disabled)",
        },
        {
            trigger:
                ".o_wsale_product_information:has(#out_of_stock_message:contains('Out of Stock')) a:contains('Test Product 7')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger:
                "#product_details #out_of_stock_message:contains('Out of Stock')",
        },
        {
            trigger:
                ".o_wsale_product_information:has(.btn-primary.disabled) a:contains('Test Product 7')",
        },
    ];

    tour.register(
        "website_sale_stock_list_preview",
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
