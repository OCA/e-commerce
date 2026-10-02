/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {ProductMatrixDialog} from "@website_sale_product_matrix/js/product_configurator/product_matrix_dialog.esm";
import {onMounted} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";

patch(ProductMatrixDialog, {
    props: {
        ...ProductMatrixDialog.props,
        // The unit the product is sold in, 0 for its own unit of measure.
        secondaryUomId: {type: Number, optional: true},
        saveSecondaryUom: {type: Function, optional: true},
    },
});

patch(ProductMatrixDialog.prototype, {
    setup() {
        super.setup(...arguments);
        onMounted(() => {
            const select = this._getSecondaryUomSelect();
            if (!select || this.props.secondaryUomId === undefined) {
                return;
            }
            // The matrix is rendered with the default unit of the product
            const value = String(this.props.secondaryUomId || "");
            if ([...select.options].some((option) => option.value === value)) {
                select.value = value;
            }
        });
    },

    /**
     * @returns {HTMLSelectElement|null} The unit selector of the matrix.
     */
    _getSecondaryUomSelect() {
        return this.matrixRef.el.querySelector(".o_matrix_secondary_unit");
    },

    /**
     * Report the unit chosen for the whole matrix to the product configurator.
     *
     * @override
     */
    onConfirm() {
        const select = this._getSecondaryUomSelect();
        if (select && this.props.saveSecondaryUom) {
            this.props.saveSecondaryUom(parseInt(select.value, 10) || 0);
        }
        return super.onConfirm(...arguments);
    },
});
