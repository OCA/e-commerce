/* Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
 * Copyright 2023 Pilar Vargas <pilar.vargas@tecnativa.com>
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import * as tourUtils from "@website_sale/js/tours/tour_utils";
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_require_legal_with_payment", {
    url: "/shop",
    steps: () => [
        ...tourUtils.searchProduct("Legal Test Product", {select: true}),
        {
            content: "click on add to cart",
            trigger: "#product_detail form #add_to_cart",
            run: "click",
        },
        tourUtils.goToCart(),
        tourUtils.goToCheckout(),
        // Fill all required fields except legal terms acceptance
        {
            content: "Fulfill delivery address form",
            trigger: 'select[name="country_id"]',
            run: "selectByLabel Spain",
        },
        {
            trigger: `input[name="name"]`,
            run: "edit ghi",
        },
        {
            trigger: `input[name="phone"]`,
            run: "edit 99999999",
        },
        {
            trigger: `input[name="vat"]`,
            run: "edit BE04774722701",
        },
        {
            trigger: `input[name="street"]`,
            run: "edit Castle St., 1",
        },
        {
            trigger: `input[name="city"]`,
            run: "edit Mushroom Kingdom",
        },
        {
            trigger: `input[name="zip"]`,
            run: "edit 100",
        },
        {
            trigger: `input[name="email"]`,
            run: "edit super_mario@odoo.com",
        },
        {
            content: "Try to continue without accepting legal terms",
            trigger: "a[name='website_sale_main_button']",
            run: "click",
        },
        {
            trigger: "#accepted_legal_terms",
            run: "click",
        },
        {
            content: "Continue after accepting legal terms",
            trigger: "a[name='website_sale_main_button']",
            run: "click",
            expectUnloadPage: true,
        },
        tourUtils.confirmOrder(),
        // If I can proceed to payment, it's because the form validated fine
        {
            trigger: "#website_sale_tc_checkbox",
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
        {
            content: "click on add to cart",
            trigger: "#product_detail form #add_to_cart",
            run: "click",
        },
        tourUtils.goToCart(),
        tourUtils.goToCheckout(),
        // Fill all required fields except legal terms acceptance
        {
            content: "Fulfill delivery address form",
            trigger: 'select[name="country_id"]',
            run: "selectByLabel Spain",
        },
        {
            trigger: `input[name="name"]`,
            run: "edit ghi",
        },
        {
            trigger: `input[name="phone"]`,
            run: "edit 99999999",
        },
        {
            trigger: `input[name="vat"]`,
            run: "edit BE04774722701",
        },
        {
            trigger: `input[name="street"]`,
            run: "edit Castle St., 1",
        },
        {
            trigger: `input[name="city"]`,
            run: "edit Mushroom Kingdom",
        },
        {
            trigger: `input[name="zip"]`,
            run: "edit 100",
        },
        {
            trigger: `input[name="email"]`,
            run: "edit super_mario@odoo.com",
        },
        {
            content: "Try to continue without accepting legal terms",
            trigger: "a[name='website_sale_main_button']",
            run: "click",
        },
        {
            trigger: "#accepted_legal_terms",
            run: "click",
        },
        {
            content: "Continue after accepting legal terms",
            trigger: "a[name='website_sale_main_button']",
            run: "click",
            expectUnloadPage: true,
        },
        tourUtils.confirmOrder(),
    ],
});
