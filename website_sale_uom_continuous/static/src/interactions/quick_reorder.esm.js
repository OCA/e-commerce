// Copyright 2026 Camptocamp (http://www.camptocamp.com).
// @author Iván Todorovich <ivan.todorovich@gmail.com>
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import {QuickReorder} from "@website_sale/interactions/quick_reorder";
import {patch} from "@web/core/utils/patch";
import {withDecimals} from "@website_sale_uom_continuous/js/utils.esm";

patch(QuickReorder.prototype, {
    /**
     * Core parses the quantity with `parseInt`, which drops its decimals:
     * https://github.com/odoo/odoo/blob/b3e4ddcbcc3a6a5a28f18f70342dcd584432faef/addons/website_sale/static/src/interactions/quick_reorder.js#L30
     * Keep them, to display the price of the typed quantity.
     *
     * @override
     */
    updateQuantityAndPrice() {
        return withDecimals(() => super.updateQuantityAndPrice(...arguments));
    },

    /**
     * Core parses the quantity with `parseInt` before sending it to the server:
     * https://github.com/odoo/odoo/blob/b3e4ddcbcc3a6a5a28f18f70342dcd584432faef/addons/website_sale/static/src/interactions/quick_reorder.js#L104
     * Keep its decimals.
     *
     * @override
     */
    reorderProduct() {
        return withDecimals(() => super.reorderProduct(...arguments));
    },
});
