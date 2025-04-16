/** @odoo-module **/

import {registry} from "@web/core/registry";
import tourUtils from "@website_sale/js/tours/tour_utils";

registry.category("web_tour.tours").add("website_sale_checkout_skip_payment", {
    test: true,
    url: "/shop",
    steps: () => [
        ...tourUtils.addToCart({productName: "Storage Box"}),
        tourUtils.goToCart({quantity: 1}),
        tourUtils.goToCheckout(),
        {
            content: "Click Confirm Button",
            trigger: "a[name='confirm_order_checkout_skip_payment']",
        },
        {
            trigger: "h4:contains('Payment Information')",
        },
        {
            content: "Check confirmation and that the cart has been left empty",
            trigger: "a:has(.my_cart_quantity:containsExact(0))",
            extra_trigger: "h4:contains('Payment Information')",
        },
    ],
});
