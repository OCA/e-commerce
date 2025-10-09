import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("shop_buy_checkout_suggest_account_website", {
    url: "/shop",
    steps: () => [
        // Shop Page
        {
            trigger: ".oe_product_cart a:first",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "#add_to_cart",
            run: "click",
        },
        {
            trigger: "button[name='website_sale_product_configurator_checkout_button']",
            run: "click",
            expectUnloadPage: true,
        },
        // Cart page
        {
            trigger: "a.btn-primary[href='/web/login?redirect=/shop/checkout']",
            run: "click",
            expectUnloadPage: true,
        },
        // Login Page
        {
            trigger: "#login",
            run: "fill portal",
        },
        {
            trigger: "#password",
            run: "fill portal",
        },
        {
            trigger: "button.btn-primary:first",
            run: "click",
            expectUnloadPage: true,
        },
        // Checkout Page
        {
            trigger: "a[href='/shop/payment']",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "#payment_method",
        },
        // The End
    ],
});
