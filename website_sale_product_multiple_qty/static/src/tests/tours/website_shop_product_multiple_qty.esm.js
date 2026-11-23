import {registry} from "@web/core/registry";
import configuratorTourUtils from "@sale/js/tours/product_configurator_tour_utils";
import * as tourUtils from "@website_sale/js/tours/tour_utils";

// Shop product page:
// - desk from steel: sale multiple = 5
// - desk from aluminium: no multiple (step = 1)
// Optional products in configurator:
// - chair from steel: sale multiple = 13
registry.category("web_tour.tours").add("tour_shop_product_multiple_qty", {
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
            content: "Desk white: initial qty should be 5",
            trigger: '#product_detail form input[name="add_qty"]:value(5)',
        },
        {
            content: "Desk white: plus (5 -> 10)",
            trigger: "a.js_add_cart_json:has(i.oi-plus)",
            run: "click",
        },
        {
            content: "Desk white: plus (10 -> 15)",
            trigger: "a.js_add_cart_json:has(i.oi-plus)",
            run: "click",
        },
        {
            content: "Click on add to cart",
            trigger: "#add_to_cart",
            run: "click",
        },
        configuratorTourUtils.assertProductQuantity(
            "website_sale_cart_product_desk_steel_white",
            15
        ),
        {
            content: "Close configurator",
            trigger: ".btn-close",
            run: "click",
        },
        {
            content: "Desk white: minus (15 -> 10)",
            trigger: "a.js_add_cart_json:has(i.oi-minus)",
            run: "click",
        },
        {
            content: "Desk white: minus (10 -> 5)",
            trigger: "a.js_add_cart_json:has(i.oi-minus)",
            run: "click",
        },
        {
            content: "Click on add to cart",
            trigger: "#add_to_cart",
            run: "click",
        },
        configuratorTourUtils.assertProductQuantity(
            "website_sale_cart_product_desk_steel_white",
            5
        ),
        {
            content: "Close configurator",
            trigger: ".btn-close",
            run: "click",
        },

        // Manual input: 7 -> 10 (round UP on Enter)
        {
            content: "Desk white: manual input 7 should round UP -> 10",
            trigger: '#product_detail form input[name="add_qty"]',
            run: "edit 7",
        },
        {
            content: "Desk white: press Enter to apply rounding",
            trigger: '#product_detail form input[name="add_qty"]',
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
            content: "Desk white: qty is 10",
            trigger: '#product_detail form input[name="add_qty"]:value(10)',
        },
        {
            content: "Click on add to cart",
            trigger: "#add_to_cart",
            run: "click",
        },
        configuratorTourUtils.assertProductQuantity(
            "website_sale_cart_product_desk_steel_white",
            10
        ),
        {
            content: "Close configurator",
            trigger: ".btn-close",
            run: "click",
        },

        // ----------------------------------------------------------
        // Variant switch: NON-multiple (desk from aluminium, step 1)
        // ----------------------------------------------------------
        {
            content: "click on the second variant",
            trigger: 'input[data-attribute-name="Legs"][data-value-name="Aluminium"]',
            run: "click",
        },
        {trigger: "#product_detail"},
        {
            content: "Desk aluminium (non-multiple): step is 1",
            trigger:
                '#product_detail form input[name="add_qty"][data-sale-multiple-qty="1"]',
        },
        {
            content: "Desk aluminium (non-multiple): data-is-multiple is 0",
            trigger: '#product_detail form input[name="add_qty"][data-is-multiple="0"]',
        },

        // Switch back to multiple (desk from steel) to check that initial qty is reset to 5
        {
            content: "click on the first variant",
            trigger: 'input[data-attribute-name="Legs"][data-value-name="Steel"]',
            run: "click",
        },
        {trigger: "#product_detail"},
        {
            content: "Desk white (multiple): step is 5",
            trigger:
                '#product_detail form input[name="add_qty"][data-sale-multiple-qty="5"]',
        },
        {
            content: "Desk white (multiple): data-is-multiple is 1",
            trigger: '#product_detail form input[name="add_qty"][data-is-multiple="1"]',
        },

        // ------------------------------------------
        // Configurator: desk from steel (multiple 5)
        // ------------------------------------------
        {
            content: "Click on add to cart",
            trigger: "#add_to_cart",
            run: "click",
        },
        configuratorTourUtils.assertProductQuantity(
            "website_sale_cart_product_desk_steel_white",
            5
        ),

        // Manual 7 -> 10 (round up to next multiple of 5)
        configuratorTourUtils.setProductQuantity(
            "website_sale_cart_product_desk_steel_white",
            7
        ),
        configuratorTourUtils.assertProductQuantity(
            "website_sale_cart_product_desk_steel_white",
            10
        ),

        // Plus/minus should move by 5 (10 -> 15 -> 10)
        {
            content: "Main: click plus (10 -> 15)",
            trigger: 'button[name="sale_quantity_button_plus"]',
            run: "click",
        },
        configuratorTourUtils.assertProductQuantity(
            "website_sale_cart_product_desk_steel_white",
            15
        ),
        {
            content: "Main: click minus (15 -> 10)",
            trigger: 'button[name="sale_quantity_button_minus"]',
            run: "click",
        },
        configuratorTourUtils.assertProductQuantity(
            "website_sale_cart_product_desk_steel_white",
            10
        ),

        // ---------------------------------------------------------
        // Configurator: optional product (chair white, multiple 13)
        // ---------------------------------------------------------
        configuratorTourUtils.addOptionalProduct(
            "website_sale_cart_product_chair_white"
        ),

        // Manual 7 -> 13 (round up to next multiple of 13)
        configuratorTourUtils.setProductQuantity(
            "website_sale_cart_product_chair_white",
            7
        ),
        configuratorTourUtils.assertProductQuantity(
            "website_sale_cart_product_chair_white",
            13
        ),

        // Close configurator (leave it clean)
        {
            content: "Close configurator",
            trigger: ".btn-close",
            run: "click",
        },
    ],
});
