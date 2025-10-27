/* Copyright 2025 Tecnativa - Pilar Vargas
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {registry} from "@web/core/registry";
import * as tourUtils from "@website_sale/js/tours/tour_utils";

registry.category("web_tour.tours").add("website_sale_acquirer_confirm_order", {
    url: "/shop",
    steps: () => [
        ...tourUtils.searchProduct("Customizable Desk"),
        {
            content: "select Customizable Desk",
            trigger: '.oe_product_cart:first a:contains("Customizable Desk")',
            run: "click",
        },
        {
            content: "click on add to cart",
            trigger: '#product_detail form[action^="/shop/cart/update"] #add_to_cart',
            run: "click",
        },
        {
            content: "Proceed to checkout",
            trigger: "button:contains(Proceed to Checkout)",
            run: "click",
        },
        tourUtils.goToCart({quantity: 1}),
        tourUtils.goToCheckout(),
        tourUtils.confirmOrder(),
        ...tourUtils.pay({expectUnloadPage: true, waitFinalizeYourPayment: true}),
        {
            content: "Confirmation page should be shown",
            trigger: "#oe_structure_website_sale_confirmation_1:not(:visible)",
        },
    ],
});
