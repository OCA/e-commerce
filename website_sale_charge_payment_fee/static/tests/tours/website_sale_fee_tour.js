/** @odoo-module **/

odoo.define(
    "website_sale_charge_payment_fee.tour",
    ["web_tour.tour"],
    function (require) {
        const tour = require("web_tour.tour");

        const steps = [
            {
                content: "search conference chair",
                trigger: 'form input[name="search"]',
                run: "text conference chair",
            },
            {
                content: "click search button",
                trigger: 'form:has(input[name="search"]) .oe_search_button',
            },
            {
                content: "select conference chair product",
                trigger: '.oe_product_cart:first a:contains("Conference Chair")',
            },
            {
                content: "select Conference Chair Steel",
                extra_trigger: "#product_detail",
                trigger: "label:contains('Steel') input",
            },
            {
                id: "add_cart_step",
                content: "click on add to cart",
                extra_trigger: "label:contains('Steel') input:propChecked",
                trigger:
                    '#product_detail form[action^="/shop/cart/update"] #add_to_cart',
            },
            {
                content: "Proceed to Checkout",
                trigger: "button:contains('Proceed to Checkout')",
            },
            {
                content: "express checkout link",
                trigger: 'a[href*="/shop/checkout?express=1"]',
            },
            {
                content: "select wire transfer payment",
                trigger: '#payment_method label:contains("Wire Transfer")',
            },
            {
                content: "click Pay Now",
                extra_trigger:
                    '#payment_method label:contains("Wire Transfer") input:checked,' +
                    '#payment_method:not(:has("input:radio:visible"))',
                trigger:
                    'button[name="o_payment_submit_button"]:visible:not(:disabled)',
            },
            {
                content: "finish (transfer details page)",
                trigger:
                    '.oe_website_sale:contains("Please use the following transfer details")',
                run: () => (window.location.href = "/contactus"),
                timeout: 30000,
            },
            {
                content: "wait page loaded",
                trigger: 'h1:contains("Contact us")',
                run: () => console.log("Payment‑fee tour finished successfully"),
            },
        ];

        tour.register(
            "website_sale_order_payment_fee_tour",
            {
                test: true,
                url: "/shop",
            },
            steps
        );
    }
);
