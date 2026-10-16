/* Copyright 2025 Tecnativa - Pilar Vargas
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import * as tourUtils from "@website_sale/js/tours/tour_utils";
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_acquirer_confirm_order", {
    url: "/shop",
    steps: () => [
        ...tourUtils.searchProduct("Customizable Desk", {select: true}),
        {
            content: "Add to cart",
            trigger: '.js_product button[name="add_to_cart"]',
            run: "click",
        },
        {
            content: "Check if the button is disabled",
            trigger: '.js_product button[name="add_to_cart"].pe-none',
        },
        {
            content: "Go to cart (or proceed from configurator modal)",
            trigger:
                'button[name="website_sale_product_configurator_checkout_button"], .modal button:contains("Go to Checkout"), a sup.my_cart_quantity:text(1)',
            run: "click",
            expectUnloadPage: true,
        },
        tourUtils.goToCheckout(),
        tourUtils.confirmOrder(),
        {
            content: "Select Wire Transfer payment method",
            trigger:
                'input[name="o_payment_radio"][data-payment-method-code="wire_transfer"]',
            run: "click",
        },
        ...tourUtils.pay({expectUnloadPage: true, waitFinalizeYourPayment: true}),
        {
            content: "Confirmation page should be shown",
            trigger: "#oe_structure_website_sale_confirmation_1:not(:visible)",
        },
    ],
});
