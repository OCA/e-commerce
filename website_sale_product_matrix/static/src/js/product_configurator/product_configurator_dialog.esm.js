/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {ProductConfiguratorDialog} from "@sale/js/product_configurator_dialog/product_configurator_dialog";
import {ProductMatrixDialog} from "./product_matrix_dialog.esm";
import {formatCurrency} from "@web/core/currency";
import {patch} from "@web/core/utils/patch";
import {rpc} from "@web/core/network/rpc";
import {useService} from "@web/core/utils/hooks";
import {useSubEnv} from "@odoo/owl";

patch(ProductConfiguratorDialog, {
    props: {
        ...ProductConfiguratorDialog.props,
        // Filled in with the variants of the matrix, to reach the cart request.
        matrixSelection: {type: Object, optional: true},
    },
});

patch(ProductConfiguratorDialog.prototype, {
    setup() {
        super.setup(...arguments);
        this.dialogService = useService("dialog");
        useSubEnv({openProductMatrix: this._openProductMatrix.bind(this)});
    },

    /**
     * Only the main product can be added through its matrix in the shop.
     *
     * @param {Object} product
     * @returns {Boolean}
     */
    _isMatrixProduct(product) {
        return Boolean(
            this.props.isFrontend &&
                product?.is_matrix &&
                product.product_tmpl_id === this.env.mainProductTmplId
        );
    },

    /**
     * Open the matrix of the product, filled in with the variants already
     * configured, to choose the ones to add to the cart.
     *
     * @param {Number} productTmplId - The product, as a `product.template` id.
     */
    async _openProductMatrix(productTmplId) {
        const product = this._findProduct(productTmplId);
        const {html, matrix} = await rpc("/website_sale_product_matrix/get_matrix", {
            product_template_id: productTmplId,
        });
        const quantities = new Map(
            (product.matrix_lines || []).map((line) => [
                String(line.ptav_ids),
                line.qty,
            ])
        );
        for (const cell of matrix.flat()) {
            if (cell.ptav_ids) {
                cell.qty = quantities.get(String(cell.ptav_ids)) || 0;
            }
        }
        this.dialogService.add(ProductMatrixDialog, {
            html,
            rows: matrix,
            save: (lines) => {
                product.matrix_lines = lines;
            },
        });
    },

    /**
     * The main product is only added through the variants of its matrix.
     *
     * @override
     */
    isPossibleConfiguration() {
        const mainProduct = this._findProduct(this.env.mainProductTmplId);
        if (this._isMatrixProduct(mainProduct) && !mainProduct.matrix_lines?.length) {
            return false;
        }
        return super.isPossibleConfiguration(...arguments);
    },

    /**
     * @override
     */
    getFormattedTotal() {
        if (!this.state.products.some((product) => this._isMatrixProduct(product))) {
            return super.getFormattedTotal(...arguments);
        }
        const total = this.state.products.reduce((sum, product) => {
            if (this._isMatrixProduct(product)) {
                return (product.matrix_lines || []).reduce(
                    (lineSum, line) => lineSum + line.unit_price * line.qty,
                    sum
                );
            }
            return sum + product.price * product.quantity;
        }, 0);
        return formatCurrency(total, this.currency.id);
    },

    /**
     * Report the variants of the matrix to the cart request.
     *
     * @override
     */
    async onConfirm() {
        const mainProduct = this._findProduct(this.env.mainProductTmplId);
        if (this.props.matrixSelection && this._isMatrixProduct(mainProduct)) {
            this.props.matrixSelection.matrix_changes = mainProduct.matrix_lines.map(
                ({ptav_ids, qty}) => ({ptav_ids, qty})
            );
        }
        return super.onConfirm(...arguments);
    },
});
