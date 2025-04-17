import * as tourUtils from "@website_sale/js/tours/tour_utils";
import configuratorTourUtils from "@sale/js/tours/product_configurator_tour_utils";
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("payment_fee_tour", {
    test: true,
    url: "/shop",
    steps: () => [
        ...tourUtils.addToCart({
            productName: "Conference Chair",
            expectUnloadPage: true,
        }),
        configuratorTourUtils.setProductQuantity("Conference Chair", 3),
        {
            content: "Proceed to checkout",
            trigger: "button:contains(Proceed to Checkout)",
            run: "click",
            expectUnloadPage: true,
        },
        tourUtils.goToCheckout(),
        tourUtils.confirmOrder(),
    ],
});
