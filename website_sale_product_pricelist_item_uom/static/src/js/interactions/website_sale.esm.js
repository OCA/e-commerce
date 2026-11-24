import {patch} from "@web/core/utils/patch";
import {WebsiteSale} from "@website_sale/interactions/website_sale";

patch(WebsiteSale.prototype, {
    /**
     * Override to listen to the packaging buttons.
     *
     * @override
     */
    setup() {
        super.setup(...arguments);
        Object.assign(this.dynamicContent, {
            ".o_packaging_button": {
                "t-on-mouseenter": this.onHoverPackagingButton,
                "t-on-mouseleave": this.onMouseLeavePackagingButton,
                "t-on-click": this.onMouseLeavePackagingButton,
            },
        });
    },

    /**
     * Display the price of the hovered packaging, when it differs from the
     * price of the currently selected one.
     *
     * @param {MouseEvent} ev
     */
    onHoverPackagingButton(ev) {
        const parent = ev.target.closest(".js_product");
        const priceEl = parent.querySelector('p[name="packaging_price_value"]');
        if (!priceEl) {
            return;
        }
        const hoveredPrice = parseFloat(
            ev.target.querySelector('input[name="uom_id"]').dataset.packagingPrice
        );
        const currentPrice = this._getUoMPrice(parent);
        if (Number(currentPrice.toFixed(2)) === Number(hoveredPrice.toFixed(2))) {
            return;
        }
        priceEl.querySelector(".oe_currency_value").textContent =
            this._priceToStr(hoveredPrice);
        parent.querySelector('span[name="packaging_price"]').classList.remove("d-none");
    },

    /**
     * Restore the price of the selected packaging.
     *
     * @param {MouseEvent} ev
     */
    onMouseLeavePackagingButton(ev) {
        const parent = ev.target.closest(".js_product");
        parent.querySelector('span[name="packaging_price"]')?.classList.add("d-none");
    },

    /**
     * Override to refresh the packaging prices on combination change.
     *
     * @override
     */
    _onChangeCombination(ev, parent, combination) {
        const res = super._onChangeCombination(...arguments);
        if ("packaging_prices" in combination) {
            this._handlePackagingInfo(parent, combination);
        }
        return res;
    },

    /**
     * Return the price of the currently selected packaging.
     *
     * @private
     * @param {Element} element
     * @returns {float}
     */
    _getUoMPrice(element) {
        return parseFloat(
            element.querySelector('input[name="uom_id"]:checked')?.dataset
                .packagingPrice
        );
    },

    /**
     * Store the price of each packaging on its own radio input.
     *
     * @private
     * @param {Element} parent
     * @param {Object} combination
     */
    _handlePackagingInfo(parent, combination) {
        Object.entries(combination.packaging_prices).forEach(([uomId, price]) => {
            const el = parent.querySelector(`input[name="uom_id"]#uom-${uomId}`);
            if (el) {
                el.dataset.packagingPrice = price;
            }
        });
    },
});
