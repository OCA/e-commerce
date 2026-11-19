/** @odoo-module **/
/* Copyright 2025 Tecnativa - Pilar Vargas
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {registry} from "@web/core/registry";
import tourUtils from "@website_sale/js/tours/tour_utils";

registry.category("web_tour.tours").add("website_sale_acquirer_confirm_order", {
    test: true,
    url: "/shop",
    steps: () => [
        ...tourUtils.searchProduct("Storage Box"),
        {
            content: "select Storage Box",
            trigger: '.oe_product_cart:first a:contains("Storage Box")',
        },
        {
            content: "click on add to cart",
            trigger: '#product_detail form[action^="/shop/cart/update"] #add_to_cart',
        },
        tourUtils.goToCart({quantity: 1}),
        tourUtils.goToCheckout(),
        {
            content: "Select Wire Transfer payment method",
            trigger:
                'input[name="o_payment_radio"][data-payment-method-code="wire_transfer"]',
        },
        tourUtils.pay(),
        {
            content: "Confirmation page should be shown",
            trigger: "h4:contains('Payment Information')",
            isCheck: true,
        },
    ],
});
