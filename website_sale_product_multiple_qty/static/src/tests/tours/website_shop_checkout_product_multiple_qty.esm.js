import {registry} from "@web/core/registry";
import * as tourUtils from "@website_sale/js/tours/tour_utils";

// Cart page:
// - desk from steel: sale multiple = 5
registry.category("web_tour.tours").add("tour_shop_checkout_product_multiple_qty", {
    url: "/shop",
    steps: () => [
        // ------------------------------------------------
        // Product page: MULTIPLE (desk from steel, step 5)
        // ------------------------------------------------
        ...tourUtils.searchProduct("website_sale_cart_product_desk_steel_white", {
            select: true,
        }),
        {trigger: "#product_detail"},
        {
            content: "click on add to cart",
            trigger: "#product_detail form #add_to_cart, #add_to_cart",
            run: "click",
        },
        {
            content: "click in modal on 'Checkout' button (go to cart)",
            trigger: 'button:contains("Checkout"), a:contains("Checkout")',
            run: "click",
            expectUnloadPage: true,
        },

        // Cart is loaded and qty is initially rounded to 5
        {
            content: "Cart: qty should be 5",
            trigger: "#cart_products input.js_quantity:value(5)",
        },

        // Plus/minus should move by 5 (5 -> 10 -> 15 -> 10)
        {
            content: "Cart: click plus (5 -> 10)",
            trigger:
                '#cart_products .o_cart_product .css_quantity[name="website_sale_cart_line_quantity"] a:has(i.oi.oi-plus)',
            run: "click",
        },
        {
            content: "Cart: qty is 10",
            trigger: "#cart_products input.js_quantity:value(10)",
        },
        {
            content: "Cart: click plus (10 -> 15)",
            trigger:
                '#cart_products .o_cart_product .css_quantity[name="website_sale_cart_line_quantity"] a:has(i.oi.oi-plus)',
            run: "click",
        },
        {
            content: "Cart: qty is 15",
            trigger: "#cart_products input.js_quantity:value(15)",
        },
        {
            content: "Cart: click minus (15 -> 10)",
            trigger:
                '#cart_products .o_cart_product .css_quantity[name="website_sale_cart_line_quantity"] a:has(i.oi.oi-minus)',
            run: "click",
        },
        {
            content: "Cart: qty is 10",
            trigger: "#cart_products input.js_quantity:value(10)",
        },
        {
            content: "Cart: manual input 21",
            trigger:
                '#cart_products .o_cart_product .css_quantity[name="website_sale_cart_line_quantity"] input.js_quantity',
            run: "edit 21",
        },
        {
            content: "Cart: press Enter to apply rounding",
            trigger:
                '#cart_products .o_cart_product .css_quantity[name="website_sale_cart_line_quantity"] input.js_quantity',
            run() {
                this.anchor.dispatchEvent(
                    new KeyboardEvent("keydown", {key: "Enter", bubbles: true})
                );
                this.anchor.dispatchEvent(
                    new KeyboardEvent("keyup", {key: "Enter", bubbles: true})
                );
            },
        },
        {
            content: "Cart: qty is 25",
            trigger: "#cart_products input.js_quantity:value(25)",
        },
    ],
});
