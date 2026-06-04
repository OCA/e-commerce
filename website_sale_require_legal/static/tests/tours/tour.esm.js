/* Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
 * Copyright 2023 Pilar Vargas <pilar.vargas@tecnativa.com>
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
import * as tourUtils from "@website_sale/js/tours/tour_utils";

registry.category("web_tour.tours").add("website_sale_require_legal_with_payment", {
    url: "/shop",
    steps: () => [
        ...tourUtils.addToCart({
            productName: "Storage Box",
            expectUnloadPage: true,
        }),

        tourUtils.goToCart(),
        tourUtils.goToCheckout(),
        // Fill all required fields except legal terms acceptance
        {
            content: "edit billing address",
            trigger: 'a[href^="/shop/address"][href*="address_type=billing"]:visible',
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "#o_country_id",
            run: function () {
                $('input[name="name"]').val("super_mario");
                $('input[name="phone"]').val("99999999");
                $('input[name="email"]').val("super_mario@mail.com");
                // Required for test compatibility with the website_sale_vat_required module
                $('input[name="vat"]').val("BE04774722701");
                $('input[name="street"]').val("Castle St., 1");
                $('input[name="city"]').val("Mushroom Kingdom");
                $('input[name="zip"]').val("10000");
                $("#o_country_id option:eq(1)").attr("selected", true);
            },
        },
        // Submit, to prove that it is not possible to continue without accepting the legal terms
        {
            content: "legal terms checkbox is displayed",
            trigger: "#accepted_legal_terms",
        },
        {
            content: "save address without legal terms",
            trigger: 'a[name="website_sale_main_button"]:visible',
            run: "click",
        },

        // // Accept legal terms and accept again
        {
            content: "accept legal terms",
            trigger: "#accepted_legal_terms",
            run: "click",
        },
        {
            content: "save address with legal terms",
            trigger: 'a[name="website_sale_main_button"]:visible',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "go to checkout",
            trigger: 'a[name="website_sale_main_button"]:visible',
            run: "click",
            expectUnloadPage: false,
        },
        // If I can proceed to payment, it's because the form validated fine

        tourUtils.confirmOrder(),
        ...tourUtils.pay({expectUnloadPage: true, waitFinalizeYourPayment: true}),
    ],
});

registry.category("web_tour.tours").add("website_sale_require_legal", {
    url: "/shop",
    steps: () => [
        ...tourUtils.addToCart({
            productName: "Storage Box",
            expectUnloadPage: true,
        }),
        tourUtils.goToCart({quantity: 1}),
        tourUtils.goToCheckout(),
        // Fill all required fields except legal terms acceptance
        {
            content: "edit delivery address",
            trigger:
                'a.js_edit_address[name="card_address_ref"]' +
                '[href*="address_type=delivery"]' +
                '[href*="use_delivery_as_billing="]:visible',
            run: "click",
            expectUnloadPage: true,
        },

        {
            content: "Fill delivery address form",
            trigger: "#o_country_id",
            run: "selectByLabel United States",
        },
        {
            content: "Fill delivery address form",
            trigger: "#o_state_id",
            run: "selectByLabel Florida",
        },
        {
            trigger: "#o_country_id",
            run: function () {
                $('input[name="phone"]').val("99999999");
                // Required for test compatibility with the website_sale_vat_required module
                $('input[name="vat"]').val("41511545146");
                $('input[name="street"]').val("Castle St., 1");
                $('input[name="city"]').val("Mushroom Kingdom");
                $('input[name="zip"]').val("10000");
            },
        },
        // Submit, to prove that it is not possible to continue without accepting the legal terms
        {
            content: "save address without legal terms",
            trigger: 'a[name="website_sale_main_button"]:visible',
            run: "click",
        },
        // // Accept legal terms and accept again
        {
            content: "accept legal terms",
            trigger: "#accepted_legal_terms",
            run: "click",
        },
        {
            content: "save address with legal terms",
            trigger: 'a[name="website_sale_main_button"]:visible',
            run: "click",
        },
        {
            content: "confirm checkout",
            trigger: 'a[name="website_sale_main_button"]:visible',
            run: "click",
            expectUnloadPage: true,
        },
    ],
});
