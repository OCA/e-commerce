/** @odoo-module */
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_wishlist_hide_price_tour", {
    test: true,
    url: "/shop",
    steps: () => [
        {
            trigger: ".oe_product_cart:contains('Customizable') .o_add_wishlist",
        },
        {
            trigger: "a[href='/shop/wishlist']",
        },
        {
            trigger:
                "tr:has(a:contains('Customizable Desk')):not(:has(button.o_wish_add)):not(:has(span.oe_currency_value))",
        },
    ],
});
