/* Copyright 2020 Tecnativa - Ernesto Tejeda
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
import {searchProduct} from "@website_sale/js/tours/tour_utils";
import {clickOnElement} from "@website/js/tours/tour_utils";

registry.category("web_tour.tours").add("website_sale_stock_provisioning_date", {
    test: true,
    url: "/shop",
    steps: () => [
        ...searchProduct("provisioning date"),
        clickOnElement(
            "click on product test",
            '.oe_product_cart a:contains("provisioning date")'
        ),
        {
            trigger:
                ".availability_messages:has(span:contains('Next provisioning date:'))",
        },
    ],
});
