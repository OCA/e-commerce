import * as tourUtils from "@website_sale/js/tours/tour_utils";
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_checkout_skip_payment", {
    url: "/shop",
    steps: () => [
        ...tourUtils.searchProduct("Test Product", {select: true}),
        {
            content: "Add to cart",
            trigger: "#add_to_cart",
            run: "click",
        },
        tourUtils.goToCart({quantity: 1}),
        tourUtils.goToCheckout(),
        tourUtils.confirmOrder(),
        ...tourUtils.pay({expectUnloadPage: true}),
        {
            content: "Print order",
            trigger: "a[href='/shop/print']",
        },
    ],
});
