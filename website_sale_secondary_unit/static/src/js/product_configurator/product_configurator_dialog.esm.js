/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {ProductConfiguratorDialog} from "@sale/js/product_configurator_dialog/product_configurator_dialog";
import {patch} from "@web/core/utils/patch";
import {useSubEnv} from "@odoo/owl";

patch(ProductConfiguratorDialog, {
    props: {
        ...ProductConfiguratorDialog.props,
        // Sent by the product page, where the customer already chose a unit.
        secondary_uom_id: {type: Number, optional: true},
        // Filled in with the unit chosen here, to reach the cart request.
        secondaryUomSelection: {type: Object, optional: true},
    },
});

patch(ProductConfiguratorDialog.prototype, {
    setup() {
        super.setup(...arguments);
        useSubEnv({setSecondaryUoM: this._setSecondaryUoM.bind(this)});
    },

    /**
     * Preselect the secondary unit of the main product: the one the customer
     * chose on the product page, or the default one of the product.
     *
     * @override
     */
    async _loadData() {
        const data = await super._loadData(...arguments);
        const product = data.products.find(
            (p) => p.product_tmpl_id === this.props.productTemplateId
        );
        const secondaryUomId =
            this.props.secondary_uom_id || product?.default_secondary_uom_id;
        if (product?.secondary_uoms?.length && secondaryUomId) {
            // Prices are given for the selected unit, so they have to be
            // fetched again, which requires a currency.
            this.currency.id ??= data.currency_id;
            await this._setSecondaryUoM(
                product.product_tmpl_id,
                secondaryUomId,
                product
            );
        }
        return data;
    },

    /**
     * Set the secondary unit the given product is sold in and refresh its
     * prices, which are given for one unit of the selected one.
     *
     * @param {Number} productTmplId - The product, as a `product.template` id.
     * @param {Number} secondaryUomId - The unit, as a `product.secondary.unit` id.
     * @param {Object} [loadedProduct] - The product, when not in the dialog yet.
     * @returns {Boolean} - Whether the secondary unit was updated.
     */
    async _setSecondaryUoM(productTmplId, secondaryUomId, loadedProduct) {
        const product = loadedProduct || this._findProduct(productTmplId);
        if (product.secondary_uom_id === secondaryUomId) {
            return false;
        }
        product.secondary_uom_id = secondaryUomId;
        const combination = await this._updateCombination(
            product,
            product.quantity,
            product.uom.id
        );
        product.price = parseFloat(combination.price);
        if (this.props.isFrontend) {
            product.strikethrough_price = combination.strikethrough_price
                ? parseFloat(combination.strikethrough_price)
                : 0;
        }
        return true;
    },

    /**
     * Report the chosen secondary unit to the cart request.
     *
     * @override
     */
    async onConfirm() {
        const mainProduct = this._findProduct(this.env.mainProductTmplId);
        if (this.props.secondaryUomSelection && mainProduct.secondary_uoms) {
            this.props.secondaryUomSelection.secondary_uom_id =
                mainProduct.secondary_uom_id || false;
        }
        return super.onConfirm(...arguments);
    },

    /**
     * Prices depend on the secondary unit, which belongs to the product being
     * updated, whereas the RPC params are shared by the whole dialog.
     *
     * @override
     */
    async _updateCombination(product) {
        this.updatedProduct = product;
        try {
            return await super._updateCombination(...arguments);
        } finally {
            this.updatedProduct = null;
        }
    },

    /**
     * @override
     */
    _getAdditionalRpcParams() {
        const params = super._getAdditionalRpcParams();
        if (this.updatedProduct?.secondary_uoms) {
            params.secondary_uom_id = this.updatedProduct.secondary_uom_id || 0;
        }
        return params;
    },
});
