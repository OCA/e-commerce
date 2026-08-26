/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {Product} from "@sale/js/product/product";
import {patch} from "@web/core/utils/patch";

patch(Product, {
    props: {
        ...Product.props,
        allow_uom_sell: {type: Boolean, optional: true},
        default_secondary_uom_id: {type: Number, optional: true},
        secondary_uom_id: {type: Number, optional: true},
        secondary_uoms: {type: Array, optional: true},
    },
});

patch(Product.prototype, {
    /**
     * Only the main product can be configured, so the optional ones are always
     * added to the cart in their own unit of measure.
     *
     * @returns {Boolean} Whether the customer can choose a secondary unit.
     */
    get hasSecondaryUoms() {
        return this.isMainProduct && Boolean(this.props.secondary_uoms?.length);
    },

    /**
     * @param {Event} event
     */
    selectSecondaryUoM(event) {
        this.env.setSecondaryUoM(
            this.props.product_tmpl_id,
            parseInt(event.target.value, 10)
        );
    },
});
