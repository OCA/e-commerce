import * as tourUtils from "@website_sale/js/tours/tour_utils";
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("payment_fee_tour", {
    url: "/shop",
    steps: () => [
        ...tourUtils.searchProduct("Test-1"),
        {
            content: "select Test-1",
            trigger: '.oe_product_cart:first a:contains("Test-1")',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "add 3 into cart",
            trigger: '#product_details input[name="add_qty"]',
            run: "edit 3",
        },
        {
            content: "click on add to cart",
            trigger: "#product_detail form #add_to_cart",
            run: "click",
        },
        {
            content: "Go To Cart",
            trigger: '.toast-body a:contains("View cart")',
            run: "click",
            expectUnloadPage: true,
        },
        tourUtils.goToCheckout(),
        tourUtils.confirmOrder(),
    ],
});
