/** @odoo-module */

/* Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
 * Copyright 2023 Pilar Vargas <pilar.vargas@tecnativa.com>
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
import tourUtils from "@website_sale/js/tours/tour_utils";

registry.category("web_tour.tours").add("website_sale_require_legal_with_payment", {
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
        tourUtils.goToCart(),
        tourUtils.goToCheckout(),
        // Fill all required fields except legal terms acceptance
        {
            trigger: 'select[name="country_id"]',
            run: function () {
                $('input[name="phone"]').val("99999999");
                // Required for test compatibility with the website_sale_vat_required module
                $('input[name="vat"]').val("00000000X");
                $('input[name="street"]').val("Castle St., 1");
                $('input[name="city"]').val("Mushroom Kingdom");
                $('input[name="zip"]').val("10000");
                $("#country_id option:eq(1)").attr("selected", true);
            },
        },
        // Submit, to prove that it is not possible to continue without accepting the legal terms
        {
            trigger: ".btn-primary:contains('Save address')",
        },
        // // Accept legal terms and accept again
        {
            trigger: "#accepted_legal_terms.is-invalid",
        },
        {
            trigger: ".btn-primary:contains('Save address')",
        },
        {
            trigger: "a[href='/shop/confirm_order']",
        },
        // If I can proceed to payment, it's because the form validated fine
        {
            trigger: "input[id='website_sale_tc_checkbox']",
        },
        ...tourUtils.payWithTransfer(true),
    ],
});

registry.category("web_tour.tours").add("website_sale_require_legal", {
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
        tourUtils.goToCart(),
        tourUtils.goToCheckout(),
        // Fill all required fields except legal terms acceptance
        {
            trigger: 'select[name="country_id"]',
            run: function () {
                $('input[name="phone"]').val("99999999");
                // Required for test compatibility with the website_sale_vat_required module
                $('input[name="vat"]').val("00000000X");
                $('input[name="street"]').val("Castle St., 1");
                $('input[name="city"]').val("Mushroom Kingdom");
                $('input[name="zip"]').val("10000");
                $("#country_id option:eq(1)").attr("selected", true);
            },
        },
        // Submit, to prove that it is not possible to continue without accepting the legal terms
        {
            trigger: ".btn-primary:contains('Save address')",
        },
        // // Accept legal terms and accept again
        {
            trigger: "#accepted_legal_terms.is-invalid",
        },
        {
            trigger: ".btn-primary:contains('Save address')",
        },
        {
            trigger: "a[href='/shop/confirm_order']",
        },
    ],
});
