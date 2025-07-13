/**  Copyright 2025 Kencove (http://www.kencove.com).
     @author Mohamed Alkobrosli <malkobrosly@kencove.com>
     License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). **/

/* global document setTimeout */
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_customer_reviews_tour", {
    url: "/shop/category/desks-1",
    steps: () => [
        {
            trigger: 'img[alt="Customizable Desk Test"]',
            run: "click",
        },
        {
            trigger: ".o_product_page_reviews_title",
            run: "click",
        },
        {
            trigger: ".o_product_page_reviews_title",
            run: function () {
                setTimeout(() => {
                    const next = document.querySelector(".o_next_pagination_btn");
                    next?.click();
                }, 2000);
            },
        },
        {
            trigger: ".o_product_page_reviews_title",
            run: function () {
                setTimeout(() => {
                    const next = document.querySelector(".o_previous_pagination_btn");
                    next?.click();
                }, 2000);
            },
        },
    ],
});
