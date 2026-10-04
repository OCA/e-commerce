// Copyright 2026 Camptocamp (http://www.camptocamp.com).
// @author Iván Todorovich <ivan.todorovich@gmail.com>
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import {ProductConfiguratorDialog} from "@sale/js/product_configurator_dialog/product_configurator_dialog";
import {patch} from "@web/core/utils/patch";

patch(ProductConfiguratorDialog.prototype, {
    /**
     * Only allow integer quantities for UoMs that are not continuous.
     *
     * @override
     */
    async _setQuantity(productTmplId, quantity) {
        const product = this._findProduct(productTmplId);
        const isInteger = this.props.isFrontend && !product?.uom.is_continuous;
        return super._setQuantity(
            productTmplId,
            isInteger ? Math.trunc(quantity) : quantity
        );
    },

    /**
     * Only allow integer quantities for UoMs that are not continuous.
     *
     * @override
     */
    _handleUnitOfMeasureUpdate(product) {
        super._handleUnitOfMeasureUpdate(...arguments);
        if (this.props.isFrontend && !product.uom.is_continuous) {
            product.quantity = Math.trunc(product.quantity) || 1;
        }
    },
});
