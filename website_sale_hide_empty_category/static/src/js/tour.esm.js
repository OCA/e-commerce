/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_hide_empty_category", {
    test: true,
    url: "/shop",
    steps: () => [
        {
            trigger: "#products_grid_before a:contains('Category Test Posted')",
        },
        {
            trigger:
                "#products_grid_before:not(:has(a:contains('Category Test Not Posted')))",
        },
        {
            trigger: "a[href='/shop']",
        },
        {
            trigger: ".o_wsale_filmstip_wrapper span:contains('Category Test Posted')",
        },
        {
            trigger:
                ".o_wsale_filmstip_wrapper:not(:has(span:contains('Category Test Not Posted')))",
        },
    ],
});
