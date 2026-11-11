/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

// If next dependency is not declared, the matrix methods of the dialog
// will be undefined
import "@website_sale_product_matrix/js/product_configurator/product_configurator_dialog.esm";
import {ProductConfiguratorDialog} from "@sale/js/product_configurator_dialog/product_configurator_dialog";
import {ProductMatrixDialog} from "@website_sale_product_matrix/js/product_configurator/product_matrix_dialog.esm";
import {formatCurrency} from "@web/core/currency";
import {getSelectedSecondaryUom} from "./utils.esm";
import {patch} from "@web/core/utils/patch";

patch(ProductConfiguratorDialog.prototype, {
    /**
     * As in the product page, the unit is chosen in the matrix. The matrix
     * dialog is opened through the dialog service, so it doesn't share the
     * env of the configurator: it's given the unit the product is sold in and
     * a callback to report the one finally chosen.
     *
     * @override
     */
    async _openProductMatrix(productTmplId) {
        const product = this._findProduct(productTmplId);
        if (!product.secondary_uoms?.length) {
            return super._openProductMatrix(...arguments);
        }
        const dialogService = this.dialogService;
        this.dialogService = {
            ...dialogService,
            add: (Component, props, options) =>
                dialogService.add(
                    Component,
                    Component === ProductMatrixDialog
                        ? {
                              ...props,
                              secondaryUomId: product.secondary_uom_id || 0,
                              saveSecondaryUom: (secondaryUomId) =>
                                  this._setSecondaryUoM(productTmplId, secondaryUomId),
                          }
                        : props,
                    options
                ),
        };
        try {
            return await super._openProductMatrix(...arguments);
        } finally {
            this.dialogService = dialogService;
        }
    },

    /**
     * The quantities of the matrix are typed in the secondary unit chosen in
     * it, whereas the prices of its variants are given for the product unit
     * of measure.
     *
     * @override
     */
    getFormattedTotal() {
        const mainProduct = this._findProduct(this.env.mainProductTmplId);
        const secondaryUom = getSelectedSecondaryUom(mainProduct);
        if (!this._isMatrixProduct(mainProduct) || !secondaryUom) {
            return super.getFormattedTotal(...arguments);
        }
        const total = this.state.products.reduce((sum, product) => {
            if (product === mainProduct) {
                return (product.matrix_lines || []).reduce(
                    (lineSum, line) =>
                        lineSum + line.unit_price * secondaryUom.factor * line.qty,
                    sum
                );
            }
            return sum + product.price * product.quantity;
        }, 0);
        return formatCurrency(total, this.currency.id);
    },
});
