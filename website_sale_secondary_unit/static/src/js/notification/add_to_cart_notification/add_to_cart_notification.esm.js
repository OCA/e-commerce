/* Copyright 2025 Carlos Lopez - Tecnativa
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {AddToCartNotification} from "@website_sale/js/notification/add_to_cart_notification/add_to_cart_notification";
import {patch} from "@web/core/utils/patch";

patch(AddToCartNotification.prototype, {
    /**
     * Return the product summary based on the line information.
     *
     * If the line has a secondary unit of measure,
     * the product summary is computed based on the secondary unit of measure quantity and name,
     *
     * @param {Object} line - The line element for which to return the product summary.
     * @returns {String} - The product summary.
     */
    getProductSummary(line) {
        if (line.secondary_uom_name) {
            return (
                line.secondary_uom_qty +
                " x " +
                line.secondary_uom_name +
                " " +
                line.name
            );
        }
        return super.getProductSummary(...arguments);
    },
});

const extendedShape = {
    ...AddToCartNotification.props.lines.element.shape,
    secondary_uom_name: String,
    secondary_uom_qty: {type: Number, optional: true},
};

AddToCartNotification.props = {
    ...AddToCartNotification.props,
    lines: {
        ...AddToCartNotification.props.lines,
        element: {
            ...AddToCartNotification.props.lines.element,
            shape: extendedShape,
        },
    },
};
