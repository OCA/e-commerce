/** @odoo-module **/

/* Copyright 2021 Carlos Roca
 * Copyright 2025 Tecnativa - Pilar Vargas
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_wishlist_keep", {
    test: true,
    url: "/shop",
    steps: () => [
        {
            content: "Add Test Product to wishlist from /shop",
            extra_trigger: '.oe_product_cart:contains("Test Product")',
            trigger: '.oe_product_cart:contains("Test Product") .o_add_wishlist',
        },
        {
            content: "go to wishlist",
            extra_trigger: 'a[href="/shop/wishlist"] .badge:contains(1)',
            trigger: 'a[href="/shop/wishlist"]',
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
            extra_trigger: "a:contains('Checkout')",
        },
    ],
});
