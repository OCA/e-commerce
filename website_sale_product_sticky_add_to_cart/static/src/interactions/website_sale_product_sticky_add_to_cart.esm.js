// Copyright 2026 Domatix
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import {Interaction} from "@web/public/interaction";
import {registry} from "@web/core/registry";

/**
 * Sticky add-to-cart bar for the product page.
 *
 * The bar is rendered server-side inside `website_sale.product` and hidden
 * with a CSS transform, so it never affects page scrolling. This interaction
 * only adds behaviour on top of it:
 *
 * - it toggles a visibility class past a small scroll threshold;
 * - its button forwards the click to the standard `#add_to_cart` button;
 * - a `MutationObserver` keeps the displayed price in sync when the shopper
 *   selects another variant (the standard page price is re-rendered in
 *   place by `website_sale`, the bar price is not).
 */
export class WebsiteSaleProductStickyAddToCart extends Interaction {
    static selector = "#o_sticky_add_to_cart_bar";

    setup() {
        this._onScroll = this._onScroll.bind(this);
        this._syncPrice = this._syncPrice.bind(this);
        this._onAddClick = this._onAddClick.bind(this);
        this._priceSource = document.querySelector(
            "#product_details .product_price .product_price_container"
        );
        this._priceTarget = this.el.querySelector(".o_sticky_add_to_cart_price");
    }

    start() {
        this._onAddButton = this.el.querySelector(".o_sticky_add_to_cart_add");
        if (this._onAddButton) {
            this._onAddButton.addEventListener("click", this._onAddClick);
        }
        window.addEventListener("scroll", this._onScroll, {passive: true});
        this._syncPrice();
        this._onScroll();
        if (this._priceSource && window.MutationObserver) {
            this._priceObserver = new MutationObserver(this._syncPrice);
            this._priceObserver.observe(this._priceSource, {
                childList: true,
                subtree: true,
                characterData: true,
            });
        }
    }

    destroy() {
        window.removeEventListener("scroll", this._onScroll);
        if (this._priceObserver) {
            this._priceObserver.disconnect();
        }
        if (this._onAddButton) {
            this._onAddButton.removeEventListener("click", this._onAddClick);
        }
    }

    /**
     * Reflect the currently selected variant price in the sticky bar. The
     * standard page price is the single source of truth, so both the plain
     * price and the optional crossed-out original price stay consistent with
     * what the shopper sees on the page.
     */
    _syncPrice() {
        if (this._priceSource && this._priceTarget) {
            this._priceTarget.innerHTML = this._priceSource.innerHTML;
        }
    }

    _onScroll() {
        this.el.classList.toggle("o_sticky_add_to_cart_bar_on", window.scrollY > 250);
    }

    /**
     * Trigger the regular website_sale add-to-cart flow. The bar button is a
     * plain link on purpose: delegating to the real button keeps optional
     * behaviours attached to it (quantity, bundles, custom variants) intact.
     */
    _onAddClick(ev) {
        ev.preventDefault();
        const addBtn = document.getElementById("add_to_cart");
        if (addBtn) {
            addBtn.click();
        }
    }
}

registry
    .category("public.interactions")
    .add(
        "website_sale_product_sticky_add_to_cart.sticky_add_to_cart",
        WebsiteSaleProductStickyAddToCart
    );
