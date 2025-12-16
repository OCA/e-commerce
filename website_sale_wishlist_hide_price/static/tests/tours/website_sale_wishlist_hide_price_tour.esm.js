/** @odoo-module **/

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_wishlist_hide_price_tour", {
    url: "/shop?search=Test Product",
    steps: () => [
        {
            content: `Select Test Product`,
            trigger: `.oe_product_cart:first a:text(Test Product)`,
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "click on add to wishlist",
            trigger: ".o_add_wishlist_dyn",
            run: "click",
        },
        {
            trigger: 'a[href="/shop/wishlist"] .badge:contains(1)',
        },
        {
            content: "go to wishlist",
            trigger: 'a[href="/shop/wishlist"]',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content:
                "verify that the product 'Test Product' is in the wishlist without the 'Add to Wishlist' button or price displayed",
            trigger:
                "div:has(a:contains('Test Product')):not(:has(button.o_wish_add)):not(:has(span.oe_currency_value)):visible",
        },
    ],
});
