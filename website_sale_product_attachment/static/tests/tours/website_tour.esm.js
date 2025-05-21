/** @odoo-module */
/* Copyright 2025 Tecnativa - Pilar Vargas
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_product_attachment_tour", {
    test: true,
    url: "/shop",
    steps: () => [
        {
            trigger: "a:contains('Customizable Desk')",
        },
        {
            trigger: "a:contains('Product downloads')",
        },
    ],
});
