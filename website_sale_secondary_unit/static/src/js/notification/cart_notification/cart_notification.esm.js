/* Copyright 2025 Carlos Lopez - Tecnativa
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {CartNotification} from "@website_sale/js/notification/cart_notification/cart_notification";

const extendedShape = {
    ...CartNotification.props.lines.element.shape,
    secondary_uom_name: String,
    secondary_uom_qty: {type: Number, optional: true},
};

CartNotification.props = {
    ...CartNotification.props,
    lines: {
        ...CartNotification.props.lines,
        element: {
            ...CartNotification.props.lines.element,
            shape: extendedShape,
        },
    },
};
