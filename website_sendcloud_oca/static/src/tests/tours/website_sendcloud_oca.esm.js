/** @odoo-module **/

import {registry} from "@web/core/registry";
import wsTourUtils from "@website_sale/js/tours/tour_utils";

registry.category("web_tour.tours").add("website_sendcloud_oca", {
    test: true,
    url: "/shop",
    steps: () => [
        ...wsTourUtils.addToCart({productName: "Acoustic Bloc Screens"}),
        wsTourUtils.goToCart(1),
        wsTourUtils.goToCheckout(),
        {
            content: "select delivery method 1",
            trigger: "li label:contains(UPS Standard to Access Point 0-3kg)",
        },
        {
            content: "select service point",
            trigger:
                '.o_delivery_carrier_select:contains("UPS Standard to Access Point 0-3kg") .o_website_sendcloud_btn',
        },
        {
            content: "Check that we are on checkout page",
            trigger: ".o_delivery_carrier_select",
            isCheck: true,
        },
    ],
});
