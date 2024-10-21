/** @odoo-module **/

import {registry} from "@web/core/registry";
import * as tourUtils from "@website_sale/js/tours/tour_utils";

registry.category("web_tour.tours").add("website_sale_checkout_skip_payment", {
    url: "/shop",
    steps: () => [
        ...tourUtils.searchProduct("Storage Box"),
        {
            content: "select Storage Box",
            trigger: '.oe_product_cart:first a:contains("Storage Box")',
            run: "click",
        },
        {
            content: "click on add to cart",
            trigger: '#product_detail form[action^="/shop/cart/update"] #add_to_cart',
            run: "click",
        },
        tourUtils.goToCart({quantity: 1}),
        tourUtils.goToCheckout(),
        tourUtils.confirmOrder(),
        {
            content: "Confirm order",
            trigger: "a.a-submit[href='#']:contains('Confirm')",
            run: "click",
        },
        {
            content: "Print order",
            trigger: "a[href='/shop/print']",
        },
    ],
});
