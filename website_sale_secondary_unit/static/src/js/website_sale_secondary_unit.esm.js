/* Copyright 2019 Sergio Teruel
 * Copyright 2025 Carlos Lopez - Tecnativa
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {WebsiteSale} from "@website_sale/interactions/website_sale";
import {patch} from "@web/core/utils/patch";

const SECONDARY_UOM_SELECTOR = 'select[name="secondary_uom_id"]';

/**
 * Return the secondary unit currently selected for a product, if any.
 *
 * @param {HTMLElement} el - The product form or its `.js_product` container.
 * @returns {?{id: Number, factor: Number, uomId: Number}}
 */
function getSelectedSecondaryUom(el) {
    const select =
        el.querySelector(SECONDARY_UOM_SELECTOR) ||
        el.closest(".js_product")?.querySelector(SECONDARY_UOM_SELECTOR);
    if (!select) {
        return null;
    }
    const id = parseInt(select.value, 10);
    if (!id) {
        // The product unit of measure is selected.
        return null;
    }
    return {
        id: id,
        factor: parseFloat(select.selectedOptions[0]?.dataset.factor) || 1,
        uomId: parseInt(select.dataset.productUomId, 10),
    };
}

patch(WebsiteSale.prototype, {
    setup() {
        super.setup(...arguments);
        Object.assign(this.dynamicContent, {
            [`.js_main_product ${SECONDARY_UOM_SELECTOR}`]: {
                "t-on-change": this.onChangeAddQuantity,
            },
        });
    },

    /**
     * Prices are always given for the product unit of measure, so the quantity
     * sent to `get_combination_info` has to be converted from the secondary
     * units typed by the customer.
     *
     * @override
     */
    _getOptionalCombinationInfoParam(product) {
        const params = super._getOptionalCombinationInfoParam(...arguments);
        const secondaryUom = getSelectedSecondaryUom(product);
        if (secondaryUom) {
            const quantity =
                parseFloat(product.querySelector('input[name="add_qty"]')?.value) || 1;
            params.add_qty = quantity * secondaryUom.factor;
            params.uom_id = secondaryUom.uomId;
        }
        return params;
    },

    /**
     * Add the selected secondary unit to the payload and convert the quantity
     * to the product unit of measure, which is what the cart works with.
     *
     * @override
     */
    _updateRootProduct(form) {
        super._updateRootProduct(...arguments);
        const secondaryUom = getSelectedSecondaryUom(form);
        if (secondaryUom) {
            this.rootProduct.quantity =
                (this.rootProduct.quantity || 1) * secondaryUom.factor;
            this.rootProduct.uomId = secondaryUom.uomId;
            this.rootProduct.secondary_uom_id = secondaryUom.id;
        }
    },
});
