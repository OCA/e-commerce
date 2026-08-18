/* Copyright 2021 Carlos Roca
 * Copyright 2025 Tecnativa - Pilar Vargas
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_wishlist_keep", {
    url: "/shop?search=Test Product",
    steps: () => [
        {
            content: "hover card && click on add to wishlist",
            trigger: ".o_wsale_product_grid_wrapper:contains(Test Product)",
            run: "hover && click .o_add_wishlist",
        },
        {
            content: "The product has been successfully added to your wishlist.",
            trigger: 'a[href="/shop/wishlist"] .badge:contains(1)',
        },
        {
            content: "go to wishlist",
            trigger: 'a[href="/shop/wishlist"]',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Ensure that the option keep in wish list is ticked.",
            trigger: "#b2b_wish:checked",
        },
        {
            content: "get out of the wish list",
            trigger: "a[href='/shop']",
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "go back to wishlist",
            trigger: 'a[href="/shop/wishlist"]',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Ensure that the option to keep in the wish list remains ticked.",
            trigger: "#b2b_wish:checked",
        },
        {
            content: "Add product to cart",
            trigger: ".o_wish_add",
            run: "click",
        },
        {
            content: "Ensure that the option to keep in the wish list remains ticked.",
            trigger: "#b2b_wish:checked",
        },
        {
            content: "Go to cart",
            trigger: "a[href='/shop/cart']",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "a:contains('Test Product')",
        },
        {
            content: "go back to wishlist",
            trigger: 'a[href="/shop/wishlist"]',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Ensure that the option to keep in the wish list remains ticked.",
            trigger: "#b2b_wish:checked",
        },
    ],
});
