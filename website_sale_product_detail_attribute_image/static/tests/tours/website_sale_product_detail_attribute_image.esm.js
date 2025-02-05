/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_product_detail_attribute_image", {
    test: true,
    url: "/shop",
    steps: () => [
        {
            trigger: "a:contains('Customizable Desk')",
            run: "click",
        },
        {
            trigger:
                ".product-detail-attributes:has(span:contains('Policy One Value 1')):not(:has(span:contains('Dangerousness'))):has(span:contains('Policy One Value 1 for website'))",
        },
    ],
});
