/* Copyright 2026 Domatix
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import * as tourUtils from "@website_sale/js/tours/tour_utils";
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_product_sticky_add_to_cart", {
    url: "/shop",
    steps: () => [
        ...tourUtils.searchProduct("Sticky Bar Demo Product", {select: true}),
        {
            trigger: "#o_sticky_add_to_cart_bar",
        },
        {
            trigger: "#o_sticky_add_to_cart_bar",
            run: () => {
                window.scrollTo(0, 600);
            },
        },
        {
            trigger: "#o_sticky_add_to_cart_bar.o_sticky_add_to_cart_bar_on",
        },
        {
            trigger: "#o_sticky_add_to_cart_bar .o_sticky_add_to_cart_price",
        },
    ],
});
