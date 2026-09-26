// Copyright 2026 Camptocamp (http://www.camptocamp.com).
// @author Iván Todorovich <ivan.todorovich@gmail.com>
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import {WebsiteSale} from "@website_sale/interactions/website_sale";
import {patch} from "@web/core/utils/patch";

patch(WebsiteSale.prototype, {
    /**
     * Core sends the quantity with `parseInt` when computing the combination info:
     * https://github.com/odoo/odoo/blob/b3e4ddcbcc3a6a5a28f18f70342dcd584432faef/addons/website_sale/static/src/js/variant_mixin.js#L29
     * These params are merged after it, so the quantity keeps its decimals:
     * https://github.com/odoo/odoo/blob/b3e4ddcbcc3a6a5a28f18f70342dcd584432faef/addons/website_sale/static/src/js/variant_mixin.js#L32
     *
     * @override
     */
    _getOptionalCombinationInfoParam(parent) {
        const params = super._getOptionalCombinationInfoParam(...arguments);
        const addQty = parseFloat(parent.querySelector('input[name="add_qty"]')?.value);
        return isNaN(addQty) ? params : {...params, add_qty: addQty};
    },

    /**
     * Only allow integer quantities for UoMs that are not continuous.
     *
     * @override
     */
    _onChangeCombination(ev, parent, combination) {
        const input = parent.querySelector('input[name="add_qty"]');
        const quantity = parseFloat(input?.value);
        if (input && !combination.uom_is_continuous && !Number.isInteger(quantity)) {
            input.value = Math.max(
                Math.trunc(quantity) || 0,
                parseFloat(input.dataset.min || 1)
            );
        }
        return super._onChangeCombination(...arguments);
    },
});
