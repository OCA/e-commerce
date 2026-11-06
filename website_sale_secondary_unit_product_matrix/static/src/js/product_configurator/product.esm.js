/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import "@website_sale_product_matrix/js/product_configurator/product.esm";
import {Product} from "@sale/js/product/product";
import {getSelectedSecondaryUom} from "./utils.esm";
import {patch} from "@web/core/utils/patch";

patch(Product.prototype, {
    /**
     * @returns {String|undefined} The unit the quantities of the matrix are
     * typed in, when the customer can choose it.
     */
    get matrixUomName() {
        if (!this.isMatrixProduct || !this.hasSecondaryUoms) {
            return undefined;
        }
        return (
            getSelectedSecondaryUom(this.props)?.display_name ||
            this.props.uom.display_name
        );
    },

    /**
     * The price of the variants is given for the product unit of measure.
     *
     * @override
     */
    getFormattedMatrixLinePrice(line) {
        const secondaryUom = getSelectedSecondaryUom(this.props);
        if (!secondaryUom) {
            return super.getFormattedMatrixLinePrice(...arguments);
        }
        return super.getFormattedMatrixLinePrice({
            ...line,
            unit_price: line.unit_price * secondaryUom.factor,
        });
    },
});
