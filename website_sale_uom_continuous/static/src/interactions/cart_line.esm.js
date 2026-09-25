// Copyright 2026 Camptocamp (http://www.camptocamp.com).
// @author Iván Todorovich <ivan.todorovich@gmail.com>
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import {CartLine} from "@website_sale/interactions/cart_line";
import {patch} from "@web/core/utils/patch";
import {roundDecimals} from "@web/core/utils/numbers";
import {session} from "@web/session";

patch(CartLine.prototype, {
    /**
     * Core parses the quantity with `parseInt` before sending it to the server,
     * which drops its decimals:
     * https://github.com/odoo/odoo/blob/b3e4ddcbcc3a6a5a28f18f70342dcd584432faef/addons/website_sale/static/src/interactions/cart_line.js#L56
     * `parseInt` is replaced by `parseFloat` only while the synchronous part of
     * the core method runs, i.e. until the request is sent.
     * The server keeps integer quantities for UoMs that are not continuous.
     *
     * The quantity is also rounded, to avoid displaying floating point noise
     * (e.g. 1.6800000000000002) after using the +/- buttons.
     *
     * @override
     */
    _changeQuantity(input) {
        const quantity = parseFloat(input.value);
        if (!isNaN(quantity)) {
            input.value = roundDecimals(quantity, session.product_unit_digits ?? 2);
        }
        const originalParseInt = globalThis.parseInt;
        globalThis.parseInt = (value) => parseFloat(value);
        try {
            return super._changeQuantity(...arguments);
        } finally {
            globalThis.parseInt = originalParseInt;
        }
    },
});
