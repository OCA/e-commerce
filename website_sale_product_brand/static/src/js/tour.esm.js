/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_product_brand", {
    test: true,
    url: "/",
    steps: () => [
        {
            trigger: "a[href='/page/product_brands']",
            content: "Go to 'Product brand' page",
            expectUnloadPage: true,
            run: "click",
        },
        {
            content: "search Apple",
            trigger: 'form input[name="search"]',
            run: "edit Apple",
        },
        {
            content: "Click to search Apple",
            trigger: 'form:has(input[name="search"]) button',
            expectUnloadPage: true,
            run: "click",
        },
        {
            content: "select Apple",
            trigger: 'section a:has(span:contains("Apple"))',
            expectUnloadPage: true,
            run: "click",
        },
    ],
});
