/* Copyright 2021 Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_wishlist_keep.tour", function (require) {
    "use strict";

    const tour = require("web_tour.tour");

    const steps = [
        {
            content: "Add Test Product to wishlist from /shop",
            extra_trigger: '.oe_product_cart:contains("Test Product")',
            trigger: '.oe_product_cart:contains("Test Product") .o_add_wishlist',
        },
        {
            trigger: "a[href='/shop/wishlist']",
        },
        {
            trigger: ".o_wish_add",
        },
        {
            trigger: "#b2b_wish",
            extra_trigger: "a:contains('Test Product')",
        },
        {
            trigger: ".o_wish_add",
        },
        {
            trigger: "a[href='/shop/cart']",
        },
        {
            trigger: "a:contains('Test Product')",
            extra_trigger: "span:contains('Process Checkout')",
        },
    ];
    tour.register(
        "website_sale_wishlist_keep",
        {
            url: "/shop",
            test: true,
        },
        steps
    );
    return {
        steps: steps,
    };
});
