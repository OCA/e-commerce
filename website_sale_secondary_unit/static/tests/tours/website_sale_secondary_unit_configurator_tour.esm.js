/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_secondary_unit_configurator", {
    url: "/shop?search=Test configurable product",
    steps: () => [
        {
            trigger: "a:contains('Test configurable product')",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: 'select[name="secondary_uom_id"]',
            run: "selectByLabel Pack 3 Units",
        },
        {
            trigger: 'input[name="add_qty"]',
            run: "edit 2",
        },
        // The product has optional products, so the configurator is opened.
        {
            trigger: "#add_to_cart",
            run: "click",
        },
        // The unit chosen on the product page is kept, and can be changed.
        {
            trigger:
                ".o_sale_product_configurator_table select[name='secondary_uom_id']",
            run: "selectByLabel Box 4 Units",
        },
        {
            trigger: "button[name='website_sale_product_configurator_continue_button']",
            run: "click",
        },
        // The notification counts secondary units.
        {
            trigger: ".o_cart_item_count:contains('2')",
        },
        {
            trigger: "a[href='/shop/cart']",
            run: "click",
            expectUnloadPage: true,
        },
        // The line is sold in boxes: 2 boxes of 4 units = 8 units.
        {
            trigger:
                ".o_cart_product:contains('Box 4 Units'):contains('= 8 Units') input.js_quantity[value='2']",
        },
    ],
});
