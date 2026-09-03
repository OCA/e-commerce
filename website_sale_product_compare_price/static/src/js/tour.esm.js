/* Copyright 2026 Domatix
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import * as tourUtils from "@website_sale/js/tours/tour_utils";
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_product_compare_price", {
    url: "/shop",
    steps: () => [
        ...tourUtils.searchProduct("Compare Price Demo Product", {select: true}),
        {
            trigger: ".oe_compare_price_block:not(.d-none)",
        },
        {
            trigger: ".oe_compare_save:not(.d-none)",
            run: () => {
                const save = document.querySelector(".oe_compare_save");
                if (!save.textContent.includes("You save")) {
                    throw new Error("The saved amount is not displayed");
                }
            },
        },
        {
            trigger: ".oe_compare_badge:not(.d-none)",
        },
    ],
});
