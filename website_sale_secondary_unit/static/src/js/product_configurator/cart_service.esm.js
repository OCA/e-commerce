/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {CartService} from "@website_sale/js/cart_service";
import {patch} from "@web/core/utils/patch";

patch(CartService.prototype, {
    /**
     * The `save` callback of the configurator only forwards a fixed set of
     * keys of the serialized product, so the secondary unit can't be added to
     * the cart request from there. `additionalData` is instead spread as is,
     * both in the props of the dialog and in the request built when the
     * customer confirms it, so a mutable object shared through it lets the
     * dialog report the unit that was finally chosen.
     *
     * @override
     */
    _openProductConfigurator(
        productTemplateId,
        quantity,
        uomId,
        combination,
        productCustomAttributeValues,
        options,
        additionalData
    ) {
        return super._openProductConfigurator(
            productTemplateId,
            quantity,
            uomId,
            combination,
            productCustomAttributeValues,
            options,
            {...additionalData, secondaryUomSelection: {}}
        );
    },

    /**
     * Unwrap the values reported by the product configurator.
     *
     * @override
     */
    _makeRequest({secondaryUomSelection, ...params}) {
        return super._makeRequest({...params, ...secondaryUomSelection});
    },
});
