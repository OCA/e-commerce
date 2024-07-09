/** @odoo-module **/
/* Copyright 2020 Tecnativa - Ernesto Tejeda
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
import tourUtils from "@website_sale/js/tours/tour_utils";
import wTourUtils from "@website/js/tours/tour_utils";

registry.category("web_tour.tours").add("website_sale_stock_provisioning_date", {
    test: true,
    url: "/shop",
    steps: () => [
        ...tourUtils.searchProduct("provisioning date"),
        wTourUtils.clickOnElement(
            "click on product test",
            '.oe_product_cart a:contains("provisioning date")'
        ),
        {
            trigger: "a#add_to_cart",
            extra_trigger:
                ".availability_messages:has(span:contains('Next provisioning date:'))",
        },
    ],
});
