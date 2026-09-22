/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {Product} from "@sale/js/product/product";
import {formatCurrency} from "@web/core/currency";
import {patch} from "@web/core/utils/patch";

patch(Product, {
    props: {
        ...Product.props,
        is_matrix: {type: Boolean, optional: true},
        matrix_lines: {type: Array, element: Object, optional: true},
    },
});

patch(Product.prototype, {
    /**
     * @returns {Boolean} Whether the variants are chosen through the matrix.
     */
    get isMatrixProduct() {
        return Boolean(
            this.env.isFrontend && this.isMainProduct && this.props.is_matrix
        );
    },

    /**
     * The attributes are chosen through the matrix.
     *
     * @override
     */
    shouldShowPtal() {
        return !this.isMatrixProduct && super.shouldShowPtal(...arguments);
    },

    /**
     * @param {Object} line - A variant configured in the matrix.
     * @returns {String} The price of the line.
     */
    getFormattedMatrixLinePrice(line) {
        return formatCurrency(line.unit_price * line.qty, this.env.currency.id);
    },
});
