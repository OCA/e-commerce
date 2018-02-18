odoo.define("website_sale_one_step_checkout.tour_shop", function (require) {
    "use strict";

    var core = require("web.core");
    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var _t = core._t;

    tour.register('shop_buy_product_osc_demo', {

        name: "Buy products with the one-step-checkout",
        url: '/shop',
        test: true,
        wait_for: base.ready(),
        },
        [
            {
                // step 0
                content: "Select iPad Mini",
                trigger: 'a[itemprop="name"][href*="ipad-mini"]',
            },
            {
                //step 1
                content: "Click on 'Add to cart'",
                trigger: '#add_to_cart',
            },
            {
                //step 2
                content: "Proceed to checkout",
                trigger: 'a[href$="/shop/checkout"]',
            },
            {
                //step 3
                content: "Add new shipping address",
                trigger: '#add-shipping-address .btn',
            },
            {
                //step 3
                content: "Test with input error",
                waitFor: '.modal-body.address-form #osc-modal-form',
                trigger: '#js_confirm_address.btn',
                run: function () {
                    $("input[name='name']").val("website_sale-test-shoptest");
                }
            },
            {
                //step 4
                content: "Test without input error",
                waitFor: 'div[id="osc_billing"] .has-error',
                trigger: '#js_confirm_address.btn',
                run: function () {
                    if ($("input[name='name']").val() === ""){
                        $("input[name='name']").val("website_sale-test-shoptest");}
                    if ($("input[name='email']").val() === "")
                        $("input[name='email']").val("website_sale_test_shoptest@websitesaletest.optenerp.com");
                    $("input[name='phone']").val("123");
                    $("input[name='street']").val("xyz");
                    $("input[name='city']").val("Magdeburg");
                    $("input[name='zip']").val("39104");
                    $("select[name='country_id']").val("58");
                },
            },
            {
                // step 5
                content: 'Confirm address',
                trigger: '#js_confirm_address.btn',
            },
            {
                // step 6
                content: 'Confirm payment and wait for redirection to Confirmation page',
                trigger: '.js_payment .btn'
            },
            {
                // step 7
                content: "Finish",
                trigger: '.oe_website_sale:contains("Thank you for your order")'
            }
        ]
    );

    tour.register('shop_buy_product_osc_public', {

        name: "Buy products with the one-step-checkout",
        url: '/shop',
        test: true,
        wait_for: base.ready(),
        },
        [
            {
                // step 0
                content: "Select iPad Mini",
                trigger: 'a[itemprop="name"][href*="ipad-mini"]',
                // position: "bottom",
            },
            {
                //step 1
                content: "Click on 'Add to cart'",
                trigger: '#add_to_cart',
            },
            {
                //step 2
                content: "Proceed to checkout",
                trigger: 'a[href$="/shop/checkout"]',
            },
            {
                // step 3
                content: 'Try to pay',
                trigger: '.js_payment .btn',
            },
            {
                //step 4
                content: "Test with input error",
                trigger: '.js_payment .btn',
                run: function () {
                    $("input[name='name']").val("website_sale-test-shoptest");
                }
            },
            {
                //step 5
                content: "Test without input error",
                waitFor: 'div[id="osc_billing"] .has-error',
                trigger: '.js_payment .btn',
                run: function () {
                    if ($("input[name='name']").val() === ""){
                        $("input[name='name']").val("website_sale-test-shoptest");}
                    if ($("input[name='email']").val() === "")
                        $("input[name='email']").val("website_sale_test_shoptest@websitesaletest.optenerp.com");
                    $("input[name='phone']").val("123");
                    $("input[name='street']").val("xyz");
                    $("input[name='city']").val("Magdeburg");
                    $("input[name='zip']").val("39104");
                    $("select[name='country_id']").val("58");
                },
            },
            {
                //step 6
                content: 'Confirm payment and wait for redirection to Confirmation page',
                trigger: '.js_payment .btn'
            },
            {
                // step 7
                content: "Finish",
                trigger: '.oe_website_sale:contains("Thank you for your order")'
            }
        ]
    );
});