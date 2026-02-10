/* Copyright 2026 Tecnativa - Eduardo Ezerouali
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
import * as tourUtils from "@website_sale/js/tours/tour_utils";

registry.category("web_tour.tours").add("website_sale_checkout_address_no_save", {
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
        tourUtils.goToCart(),
        tourUtils.goToCheckout(),
        // Fill all required fields except legal terms acceptance
        {
            content: "Fill delivery address form",
            trigger: 'select[name="country_id"]',
            run: "selectByLabel United State",
        },
        {
            content: "Fill delivery address form",
            trigger: 'select[name="state_id"]',
            run: "selectByLabel Florida",
        },
        {
            trigger: 'select[name="country_id"]',
            run: function () {
                $('input[name="phone"]').val("99999999");
                // Required for test compatibility with the website_sale_vat_required module
                $('input[name="vat"]').val("BE04774722701");
                $('input[name="street"]').val("Castle St., 1");
                $('input[name="city"]').val("Mushroom Kingdom");
                $('input[name="zip"]').val("10000");
                $("#country_id option:eq(1)").attr("selected", true);
            },
        },
        {
            trigger: ".btn-primary:contains('Save address')",
            run: "click",
        },
        {
            trigger:
                "a[href='/shop/address?address_type=delivery&use_delivery_as_billing=True']",
            run: "click",
        },
        {
            content: "Fill delivery address form",
            trigger: 'select[name="country_id"]',
            run: "selectByLabel United State",
        },
        {
            content: "Fill delivery address form",
            trigger: 'select[name="state_id"]',
            run: "selectByLabel Florida",
        },
        {
            trigger: 'select[name="country_id"]',
            run: function () {
                $('input[name="name"]').val("John Jones");
                $('input[name="phone"]').val("99999999");
                $('input[name="email"]').val("john@jones.com");
                // Required for test compatibility with the website_sale_vat_required module
                $('input[name="vat"]').val("BE04774722701");
                $('input[name="street"]').val("Castle St., 1");
                $('input[name="city"]').val("Mushroom Kingdom");
                $('input[name="zip"]').val("10000");
                $("#country_id option:eq(1)").attr("selected", true);
            },
        },
        {
            trigger: "input[id='archive_address']",
            run: "click",
        },
        {
            trigger: ".btn-primary:contains('Save address')",
            run: "click",
        },
        {
            trigger: "a[href='/shop/confirm_order']",
            run: "click",
        },
        // If I can proceed to payment, it's because the form validated fine
        ...tourUtils.payWithTransfer(true),
    ],
});

registry
    .category("web_tour.tours")
    .add("website_sale_checkout_address_no_save_no_pay", {
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
                trigger:
                    '#product_detail form[action^="/shop/cart/update"] #add_to_cart',
                run: "click",
            },
            tourUtils.goToCart(),
            tourUtils.goToCheckout(),
            // Fill all required fields except legal terms acceptance
            {
                content: "Fill delivery address form",
                trigger: 'select[name="country_id"]',
                run: "selectByLabel United State",
            },
            {
                content: "Fill delivery address form",
                trigger: 'select[name="state_id"]',
                run: "selectByLabel Florida",
            },
            {
                trigger: 'select[name="country_id"]',
                run: function () {
                    $('input[name="phone"]').val("99999999");
                    // Required for test compatibility with the website_sale_vat_required module
                    $('input[name="vat"]').val("BE04774722701");
                    $('input[name="street"]').val("Castle St., 1");
                    $('input[name="city"]').val("Mushroom Kingdom");
                    $('input[name="zip"]').val("10000");
                    $("#country_id option:eq(1)").attr("selected", true);
                },
            },
            {
                trigger: ".btn-primary:contains('Save address')",
                run: "click",
            },
            {
                trigger:
                    "a[href='/shop/address?address_type=delivery&use_delivery_as_billing=True']",
                run: "click",
            },
            {
                content: "Fill delivery address form",
                trigger: 'select[name="country_id"]',
                run: "selectByLabel United State",
            },
            {
                content: "Fill delivery address form",
                trigger: 'select[name="state_id"]',
                run: "selectByLabel Florida",
            },
            {
                trigger: 'select[name="country_id"]',
                run: function () {
                    $('input[name="name"]').val("John Jones");
                    $('input[name="phone"]').val("99999999");
                    $('input[name="email"]').val("john@jones.com");
                    // Required for test compatibility with the website_sale_vat_required module
                    $('input[name="vat"]').val("BE04774722701");
                    $('input[name="street"]').val("Castle St., 1");
                    $('input[name="city"]').val("Mushroom Kingdom");
                    $('input[name="zip"]').val("10000");
                    $("#country_id option:eq(1)").attr("selected", true);
                },
            },
            {
                trigger: "input[id='archive_address']",
                run: "click",
            },
            {
                trigger: ".btn-primary:contains('Save address')",
                run: "click",
            },
            {
                trigger: "a[href='/shop/confirm_order']",
                run: "click",
            },
        ],
    });
