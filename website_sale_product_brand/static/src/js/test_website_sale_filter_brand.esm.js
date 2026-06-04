import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_filter_product_brand", {
    test: true,
    url: "/shop",
    steps: () => [
        {
            content: "Check brand",
            trigger: 'input[name="brand"]',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Brand should be checked after reload",
            trigger: 'input[name="brand"]:checked',
        },
    ],
});
