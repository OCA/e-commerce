/** @odoo-module **/

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_wishlist_hide_price_tour", {
    checkDelay: 250,
    url: "/shop?search=Customizable Desk",
    steps: () => [
        {
            content: "hover card && click on add to wishlist",
            trigger: ".o_wsale_product_grid_wrapper:contains(desk)",
            run: "hover && click .o_add_wishlist",
        },
        {
            trigger: 'a[href="/shop/wishlist"] .badge:contains(1)',
        },
        {
            content: "go to wishlist",
            trigger: 'a[href="/shop/wishlist"]',
            run: "click",
        },
        {
            content:
                "verify that the product 'Customizable Desk' is in the wishlist without the 'Add to Wishlist' button or price displayed",
            trigger:
                "tr:has(a:contains('Customizable Desk')):not(:has(button.o_wish_add)):not(:has(span.oe_currency_value)):visible",
        },
    ],
});
