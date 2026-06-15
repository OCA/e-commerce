// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import * as tourUtils from "@website_sale/js/tours/tour_utils";
import {registry} from "@web/core/registry";

const addProductAndCheckout = () => [
    ...tourUtils.searchProduct("Test Product", {select: true}),
    {
        content: "Add to cart",
        trigger: "#add_to_cart",
        run: "click",
    },
    tourUtils.goToCart({quantity: 1}),
    tourUtils.goToCheckout(),
    tourUtils.confirmOrder(),
];

registry.category("web_tour.tours").add("website_sale_require_po_doc_with_value", {
    url: "/shop",
    steps: () => [
        ...addProductAndCheckout(),
        {
            content: "PO field is visible",
            trigger: "#customer_ref_input",
        },
        {
            content: "Fill in PO number",
            trigger: "#customer_ref_input",
            run: "edit PO-12345",
        },
        {
            content: "Blur field to trigger save",
            trigger: "#div_customer_po_ref h4",
            run: "click",
        },
        {
            content: "Confirm order",
            trigger: 'form[name="o_wsale_confirm_order"] button',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Order confirmed",
            trigger: "#order_name",
        },
    ],
});

registry.category("web_tour.tours").add("website_sale_require_po_doc_without_value", {
    url: "/shop",
    steps: () => [
        ...addProductAndCheckout(),
        {
            content: "PO field is visible",
            trigger: "#customer_ref_input",
        },
        {
            content: "Try to confirm without filling PO number",
            trigger: 'form[name="o_wsale_confirm_order"] button',
            run: "click",
        },
        {
            content: "Validation error is shown",
            trigger: "#customer_ref_input.is-invalid",
        },
    ],
});

registry.category("web_tour.tours").add("website_sale_require_po_doc_not_required", {
    url: "/shop",
    steps: () => [
        ...addProductAndCheckout(),
        {
            content: "PO field is not shown on payment page",
            trigger: "#address_on_payment",
            run: () => {
                if (document.querySelector("#customer_ref_input")) {
                    throw new Error("PO field should not be visible");
                }
            },
        },
    ],
});
