/** @odoo-module */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("shop_buy_checkout_required_login_website", {
    test: true,
    url: "/shop",
    steps: () => [
        // Shop Page
        {
            trigger: "td.oe_product a:first",
        },
        // Product Page
        {
            trigger: "#add_to_cart",
        },
        {
            trigger: 'a.o_navlink_background.btn[href="/shop/cart"]',
        },
        {
            trigger: '.oe_website_sale:not(a.btn-primary[href^="/shop/checkout"])',
            run: function () {
                // Check: do nothing
            },
        },
        {
            trigger: '.oe_website_sale:not(a.btn-default[href^="/shop/checkout"])',
            run: function () {
                // Check: do nothing
            },
        },
        // The End
    ],
});
