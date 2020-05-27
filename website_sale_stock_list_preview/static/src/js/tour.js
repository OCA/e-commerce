/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_stock_list_preview.tour", function(require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger:
                ".o_wsale_product_information:has(.text-success:contains('30 Units available')) a:contains('Test Product 1')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger:
                "#product_details .text-success:contains('30 Units available')",
        },
        {
            trigger:
                ".o_wsale_product_information:not(:has(.btn-secondary.disabled)) a:contains('Test Product 1')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "#product_details a:not(#add_to_cart.disabled)",
        },
        {
            trigger:
                ".o_wsale_product_information:has(.text-success:contains('In stock')) a:contains('Test Product 2')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "#product_details .text-success:contains('In stock')",
        },
        {
            trigger:
                ".o_wsale_product_information:not(:has(.btn-secondary.disabled)) a:contains('Test Product 2')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "#product_details a:not(#add_to_cart.disabled)",
        },
        {
            trigger:
                ".o_wsale_product_information:has(.text-warning:contains('5 Units available')) a:contains('Test Product 3')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger:
                "#product_details .text-warning:contains('5 Units available')",
        },
        {
            trigger:
                ".o_wsale_product_information:not(:has(.btn-secondary.disabled)) a:contains('Test Product 3')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "#product_details a:not(#add_to_cart.disabled)",
        },
        {
            trigger:
                ".o_wsale_product_information:has(.text-success:contains('test message')) a:contains('Test Product 4')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "#product_details .text-success:contains('test message')",
        },
        {
            trigger:
                ".o_wsale_product_information:not(:has(.btn-secondary.disabled)) a:contains('Test Product 4')",
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
                ".o_wsale_product_information:not(:has(btn-secondary.disabled)) a:contains('Test Product 5')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "#product_details a:not(#add_to_cart.disabled)",
        },
        {
            trigger:
                ".o_wsale_product_information:has(.text-danger:contains(' Temporarily out of stock')) a:contains('Test Product 6')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger:
                "#product_details .text-danger:contains(' Temporarily out of stock')",
        },
        {
            trigger:
                ".o_wsale_product_information:has(.btn-secondary.disabled) a:contains('Test Product 6')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "#product_details a#add_to_cart.disabled",
        },
        {
            trigger:
                ".o_wsale_product_information:has(.text-danger:contains(' Temporarily out of stock')) a:contains('Test Product 7')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger:
                "#product_details .text-danger:contains(' Temporarily out of stock')",
        },
        {
            trigger:
                ".o_wsale_product_information:has(.btn-secondary.disabled) a:contains('Test Product 7')",
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
