/* Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
 * Copyright 2023 Pilar Vargas <pilar.vargas@tecnativa.com>
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import * as tourUtils from "@website_sale/js/tours/tour_utils";
import {registry} from "@web/core/registry";

function fillAddressAndAcceptLegalTerms() {
    return [
        {
            content: "Select the address country",
            trigger: "#o_country_id",
            run: "selectByLabel Belgium",
        },
        ...Object.entries({
            name: "Super Mario",
            phone: "99999999",
            email: "super_mario@odoo.com",
            street: "Castle St., 1",
            city: "Brussels",
            zip: "1000",
        }).map(([name, value]) => ({
            trigger: `form.address_autoformat input[name="${name}"]`,
            run: `edit ${value}`,
        })),
        {
            content: "Try to continue without accepting legal terms",
            trigger: "a[name='website_sale_main_button']",
            run: "click",
        },
        {
            content: "Check that only legal terms acceptance prevents submission",
            trigger: "#accepted_legal_terms:invalid",
            run() {
                const invalidFields = document.querySelectorAll(
                    "form.address_autoformat :invalid"
                );
                if (
                    invalidFields.length !== 1 ||
                    invalidFields[0].id !== "accepted_legal_terms"
                ) {
                    throw new Error("Only legal terms acceptance should be missing");
                }
            },
        },
        {
            content: "Accept legal terms",
            trigger: "#accepted_legal_terms",
            run: "click",
        },
        {
            content: "Continue after accepting legal terms",
            trigger: "a[name='website_sale_main_button']",
            run: "click",
            expectUnloadPage: true,
        },
    ];
}

registry.category("web_tour.tours").add("website_sale_require_legal_with_payment", {
    url: "/shop",
    steps: () => [
        ...tourUtils.searchProduct("Legal Test Product", {select: true}),
        ...tourUtils.addToCartFromProductPage(),
        tourUtils.goToCart(),
        tourUtils.goToCheckout(),
        ...fillAddressAndAcceptLegalTerms(),
        tourUtils.confirmOrder(),
        // If I can proceed to payment, it's because the form validated fine
        {
            trigger: "#website_sale_tc_checkbox:visible",
            run: "click",
        },
        ...tourUtils.payWithTransfer({
            redirect: false,
            expectUnloadPage: true,
            waitFinalizeYourPayment: true,
        }),
    ],
});

registry.category("web_tour.tours").add("website_sale_require_legal", {
    url: "/shop",
    steps: () => [
        ...tourUtils.searchProduct("Legal Test Product", {select: true}),
        ...tourUtils.addToCartFromProductPage(),
        tourUtils.goToCart(),
        tourUtils.goToCheckout(),
        ...fillAddressAndAcceptLegalTerms(),
        tourUtils.confirmOrder(),
    ],
});
