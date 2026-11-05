/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_stock_available", {
    url: "/shop?search=Storable product",
    steps: () => [
        {
            content: "Open the product page",
            trigger: "a:contains('Storable product')",
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Ask for more than the free quantity",
            trigger: "#product_details input[name='add_qty']",
            run: "edit 40",
        },
        {
            content: "Add to cart",
            trigger: "#add_to_cart",
            run: "click",
        },
        {
            content: "The whole quantity is in the cart",
            trigger: "a sup.my_cart_quantity:text(40)",
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "No availability warning in the cart",
            trigger:
                "#cart_products:not(:has(.alert-warning)) input.js_quantity:value(40)",
        },
    ],
});
