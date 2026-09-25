// Copyright 2026 Camptocamp (http://www.camptocamp.com).
// @author Iván Todorovich <ivan.todorovich@gmail.com>
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import * as tourUtils from "@website_sale/js/tours/tour_utils";
import configuratorTourUtils from "@sale/js/tours/product_configurator_tour_utils";
import {registry} from "@web/core/registry";

function cartLineQuantity(productName) {
    return `.o_cart_product:has(h6:contains("${productName}")) input.js_quantity`;
}

function configuratorQuantity(productName) {
    return `${configuratorTourUtils.productSelector(productName).trim()}
        td.o_sale_product_configurator_qty input[name="sale_quantity"]`;
}

registry.category("web_tour.tours").add("website_sale_uom_continuous", {
    url: "/shop",
    steps: () => [
        // Product page: continuous UoMs keep their decimals.
        ...tourUtils.searchProduct("Decimal Powder", {select: true}),
        {
            content: "Set 2.5 kg of powder",
            trigger: 'input[name="add_qty"]',
            run: "edit 2.5 && click body",
        },
        {trigger: "#add_to_cart", run: "click"},
        {trigger: "a sup.my_cart_quantity:text(1)"},
        {trigger: "a[href='/shop']", run: "click", expectUnloadPage: true},
        // Product page: other UoMs only allow integer quantities.
        ...tourUtils.searchProduct("Decimal Bolt", {select: true}),
        {
            content: "Set 2.5 bolts",
            trigger: 'input[name="add_qty"]',
            run: "edit 2.5 && click body",
        },
        {
            content: "The bolt quantity is truncated to an integer",
            trigger: 'input[name="add_qty"]:value(/^2$/)',
        },
        {trigger: "#add_to_cart", run: "click"},
        // Product configurator: other UoMs only allow integer quantities.
        {trigger: `${configuratorQuantity("Decimal Bolt")}:value(/^2$/)`},
        {
            content: "Set 3.7 bolts",
            trigger: configuratorQuantity("Decimal Bolt"),
            // Typed character by character, the intermediate "3." is not a valid value for a
            // number input and would be dropped, so the value is set at once.
            run() {
                this.anchor.value = "3.7";
                this.anchor.dispatchEvent(new Event("input", {bubbles: true}));
                this.anchor.dispatchEvent(new Event("change", {bubbles: true}));
            },
        },
        {
            content: "The bolt quantity is truncated to an integer",
            trigger: `${configuratorQuantity("Decimal Bolt")}:value(/^3$/)`,
        },
        {
            trigger: 'button[name="website_sale_product_configurator_continue_button"]',
            run: "click",
        },
        // Cart: the powder line counts as one item, the bolts are summed.
        tourUtils.goToCart({quantity: 4}),
        // The `value` attribute is only set when the cart lines are rendered by the server,
        // unlike the typed value.
        {trigger: `${cartLineQuantity("Decimal Powder")}[value="2.5"]`},
        {trigger: `${cartLineQuantity("Decimal Bolt")}[value="3"]`},
        {
            content: "Set 3.5 kg of powder",
            trigger: cartLineQuantity("Decimal Powder"),
            run: "edit 3.5 && click body",
        },
        {
            content: "The powder quantity keeps its decimals",
            trigger: `${cartLineQuantity("Decimal Powder")}[value="3.5"]`,
        },
        {
            content: "Set 4.7 bolts",
            trigger: cartLineQuantity("Decimal Bolt"),
            run: "edit 4.7 && click body",
        },
        {
            content: "The bolt quantity is truncated to an integer",
            trigger: `${cartLineQuantity("Decimal Bolt")}[value="4"]`,
        },
        {trigger: "a sup.my_cart_quantity:text(5)"},
        // Checkout: the summary keeps the decimals of the powder.
        tourUtils.goToCheckout(),
        {
            content: "The powder quantity keeps its decimals in the checkout summary",
            trigger: `.o_cart_products_table tr:has(.td-product_name:contains("Decimal Powder")) .o_cart_item_count:contains(3.5)`,
        },
    ],
});

function quickReorderLine(productName) {
    return `.o_wsale_quick_reorder_line:has(h6:contains("${productName}"))`;
}

registry.category("web_tour.tours").add("website_sale_uom_continuous_quick_reorder", {
    steps: () => [
        {trigger: "#quick_reorder_button", run: "click"},
        {
            content: "The previous quantity keeps its decimals",
            trigger: `${quickReorderLine("Reorder Powder")} .o_wsale_quick_reorder_qty_input:value(/^2\\.5$/)`,
        },
        {
            content: "Set 1.5 kg of powder",
            trigger: `${quickReorderLine("Reorder Powder")} .o_wsale_quick_reorder_qty_input`,
            run: "edit 1.5",
        },
        {
            content: "The price is the one of 1.5 kg",
            trigger: `${quickReorderLine("Reorder Powder")} .o_wsale_quick_reorder_qty_input`,
            run() {
                const price = this.anchor
                    .closest(".o_wsale_quick_reorder_line")
                    .querySelector(
                        ".o_wsale_quick_reorder_product_price .oe_currency_value"
                    );
                const expected = (
                    parseFloat(this.anchor.dataset.priceUnit) * 1.5
                ).toFixed(2);
                if (price.textContent !== expected) {
                    throw new Error(
                        `Expected price ${expected}, got ${price.textContent}`
                    );
                }
            },
        },
        {
            trigger: `${quickReorderLine("Reorder Powder")} .o_wsale_quick_reorder_product_button`,
            run: "click",
        },
        {
            content: "The powder is added with its decimals",
            trigger: `.o_cart_product:has(h6:contains("Reorder Powder")) input.js_quantity[value="1.5"]`,
        },
    ],
});
