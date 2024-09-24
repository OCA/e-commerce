odoo.define("website_sale_cart_clear.tour", function (require) {
    "use strict";

    const tour = require("web_tour.tour");
    const websiteSaleTourUtils = require("website_sale.tour_utils");
    const websiteTourUtils = require("website.tour_utils");

    tour.register(
        "website_sale_cart_clear_tour",
        {
            test: true,
            url: "/shop",
        },
        [
            {
                content: "Write Test Product in search box",
                trigger: "form input[name='search']",
                run: "text Test Product",
            },
            websiteTourUtils.clickOnElement(
                "Submit search",
                "form:has(input[name='search']) .oe_search_button"
            ),
            websiteTourUtils.clickOnElement(
                "Select Test Product",
                ".oe_product_cart:first a:contains('Test Product')"
            ),
            websiteTourUtils.clickOnElement("Add to cart", "#add_to_cart"),
            websiteSaleTourUtils.goToCart(),
            websiteSaleTourUtils.assertCartContains({
                productName: "Test Product",
            }),
            websiteTourUtils.clickOnElement("Remove all products", ".js_clear_cart"),
            {
                content: "Assert cart is empty",
                trigger: ".js_cart_lines:contains('Your cart is empty!')",
            },
        ]
    );
});
