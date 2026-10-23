/* Copyright 2026 ADHOC SA
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {AddToCart} from "@website_sale/interactions/add_to_cart";
import {Interaction} from "@web/public/interaction";
import {patch} from "@web/core/utils/patch";
import {registry} from "@web/core/registry";

// The tile is not a form anymore, so the quantity reaches the cart here.
patch(AddToCart.prototype, {
    _getOptionalParams() {
        const params = super._getOptionalParams(...arguments);
        if (this.el.closest(".js_product")) {
            // The core already read the quantity of the product page.
            return params;
        }
        const input = this.el
            .closest(".oe_product_cart")
            ?.querySelector('input[name="add_qty"]');
        return input ? {...params, quantity: parseFloat(input.value) || 1} : params;
    },
});

export class ProductTileQuantity extends Interaction {
    static selector = ".oe_product_cart .css_quantity";
    dynamicContent = {
        'button[name="minus_button"]': {
            "t-on-click.prevent": () => this.addQuantity(-1),
        },
        'button[name="plus_button"]': {
            "t-on-click.prevent": () => this.addQuantity(1),
        },
        'input[name="add_qty"]': {"t-on-change": () => this.addQuantity(0)},
    };

    /**
     * Add `delta` to the quantity, keeping it within the input's bounds.
     *
     * @param {Number} delta
     */
    addQuantity(delta) {
        const input = this.el.querySelector('input[name="add_qty"]');
        const min = parseFloat(input.dataset.min) || 0;
        const max = parseFloat(input.dataset.max) || Infinity;
        const previousQty = parseFloat(input.value) || min;
        const newQty = Math.min(Math.max(previousQty + delta, min), max);
        if (input.value !== String(newQty)) {
            input.value = newQty;
            input.dispatchEvent(new Event("change", {bubbles: true}));
        }
    }
}

registry
    .category("public.interactions")
    .add(
        "website_sale_product_item_cart_custom_qty.product_tile_quantity",
        ProductTileQuantity
    );
