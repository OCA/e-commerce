/* Copyright 2020 Tecnativa - Ernesto Tejeda
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
import {searchProduct} from "@website_sale/js/tours/tour_utils";

registry.category("web_tour.tours").add("website_sale_stock_provisioning_date", {
    test: true,
    url: "/shop",
    steps: () => [
        ...searchProduct("provisioning date"),
        {
            content: "click on product test",
            trigger: '.oe_product_cart a:contains("provisioning date")',
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger:
                ".availability_messages:has(span:contains('Next provisioning date:'))",
        },
    ],
});
