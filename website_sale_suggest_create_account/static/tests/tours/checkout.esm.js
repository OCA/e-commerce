import {registry} from "@web/core/registry";
registry.category("web_tour.tours").add("shop_buy_checkout_suggest_account_website", {
    url: "/shop",
    steps: () => [
        // Shop Page
        {
            trigger: "a:contains('Customizable')",
            run: "click",
        },
        {
            trigger: "#add_to_cart",
            run: "click",
        },

        {
            trigger: "button:contains('Proceed to Checkout')",
            run: "click",
        },
        // Cart page
        {
            trigger: "a.btn-primary[href='/web/login?redirect=/shop/checkout']",
            run: "click",
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
        },
        // Checkout Page
        {
            trigger: "a[href='/shop/confirm_order']",
            run: "click",
        },
        {
            trigger: "h3",
            content: "Confirm Order",
        },
        // The End
    ],
});
