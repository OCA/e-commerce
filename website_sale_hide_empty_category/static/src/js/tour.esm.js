/** @odoo-module **/

/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_hide_empty_category", {
    test: true,
    url: "/shop",
    steps: () => [
        {
            trigger: "#products_grid_before label:contains('Category Test Posted')",
            extra_trigger:
                "#products_grid_before:not(:has(label:contains('Category Test Not Posted')))",
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: ".o_wsale_filmstip_wrapper span:contains('Category Test Posted')",
            extra_trigger:
                ".o_wsale_filmstip_wrapper:not(:has(span:contains('Category Test Not Posted')))",
        },
    ],
});
