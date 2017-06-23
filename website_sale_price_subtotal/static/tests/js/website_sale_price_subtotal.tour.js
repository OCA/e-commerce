/* Copyright 2017 LasLabs Inc.
 * License LGPL-3 or later (http://www.gnu.org/licenses/lgpl.html) */

odoo.define('website_sale_price_subtotal.tour', function (require) {
    'use strict';

    var tour = require('web_tour.tour');
    var _t = require('web.core')._t;
    var base = require('web_editor.base');

    tour.register(
        'website_sale_price_subtotal',
        {
            url: '/shop',
            name: _t('Test website shop logic replacing unit prices with subtotals'),
            test: true,
            wait_for: base.ready(),
        },
        [
            {
                content: 'Search for "Website Subtotal" to find demo product',
                trigger: 'input[name="search"]',
                run: function(actions) {
                    $('input[name="search"]').val('Website Subtotal');
                    actions.click('.oe_search_button');
                },
            },
            {
                content: 'Open product page for demo product',
                trigger: 'a:contains("Website Subtotal - Demo Product")',
                run: function(actions) {
                    actions.click('a:contains("Website Subtotal - Demo Product")');
                },
            },
            {
                content: 'Change quantity to 2 using main input',
                trigger: '.css_quantity input',
                run: function() {
                    // Change event should be fired to properly replicate user action
                    $('.css_quantity input').val(2).trigger('change');
                },
            },
            {
                content: 'Check that subtotal reflects new quantity',
                trigger: '.oe_price span:contains("300")',
            },
            {
                content: 'Check that public price subtotal reflects new quantity',
                trigger: '.oe_price span:contains("300")',
                run: function() {
                    var subtotal = parseInt($('.oe_default_price span').text(), 10);
                    if (subtotal !== 600) {
                        tour._consume_tour(
                            tour.running_tour,
                            'A quantity increase did not cause the public' +
                            ' price subtotal to be updated correctly'
                        );
                    }
                },
            },
            {
                content: 'Add products to cart',
                trigger: 'a#add_to_cart',
                run: function(actions) {
                    actions.click('a#add_to_cart');
                },
            },
            {
                content: 'Return to previous page using back button',
                trigger: 'h1:contains("Shopping Cart")',
                run: function() {
                    window.history.back();
                },
            },
            {
                content: 'Check that subtotal is still correct after back button',
                trigger: '.oe_price span:contains("300")',
            },
            {
                content: 'Check public price subtotal after back button',
                trigger: '.oe_price span:contains("300")',
                run: function() {
                    var subtotal = parseInt($('.oe_default_price span').text(), 10);
                    if (subtotal !== 600) {
                        tour._consume_tour(
                            tour.running_tour,
                            'Use of the back button caused an incorrect' +
                            ' public price subtotal'
                        );
                    }
                },
            },
            {
                content: 'Select second product variant',
                trigger: 'input.js_variant_change',
                run: function(actions) {
                    actions.click('input.js_variant_change:last');
                },
            },
            {
                content: 'Check that subtotal reflects new variant',
                trigger: '.oe_price span:contains("500")',
            },
            {
                content: 'Change quantity to 1 using minus button',
                trigger: '.css_quantity i:first',
                run: function(actions) {
                    actions.click('.css_quantity i:first');
                },
            },
            {
                content: 'Check that subtotal reflects new quantity',
                trigger: '.oe_price span:contains("250")',
            },
            {
                content: 'Check that public price subtotal reflects new quantity',
                trigger: '.oe_price span:contains("250")',
                run: function() {
                    var subtotal = parseInt($('.oe_default_price span').text(), 10);
                    if (subtotal !== 300) {
                        tour._consume_tour(
                            tour.running_tour,
                            'A quantity decrease did not cause the public' +
                            ' price subtotal to be updated correctly'
                        );
                    }
                },
            },
            {
                content: 'Add product to cart',
                trigger: 'a#add_to_cart',
                run: function(actions) {
                    actions.click('a#add_to_cart');
                },
            },
            {
                content: 'Check that correct subtotals are shown in cart',
                trigger: 'td .oe_currency_value:first:contains("300")',
                extra_trigger: 'td .oe_currency_value:last:contains("250")',
            },
            {
                content: 'Change quantity of second variant to 2 using input',
                trigger: '.input-group input:last',
                run: function() {
                    // Change event should be fired to properly replicate user action
                    $('.input-group input:last').val(2).trigger('change');
                },
            },
            {
                content: 'Check that subtotals correctly reflect new quantity',
                trigger: 'td .oe_currency_value:last:contains("500")',
                extra_trigger: 'td .oe_currency_value:first:contains("300")',
            },
            {
                content: 'Change quantity of first variant to 1 using minus button',
                trigger: '.fa-minus:first',
                run: function(actions) {
                    actions.click('.fa-minus:first');
                },
            },
            {
                content: 'Check that subtotals correctly reflect new quantity',
                trigger: 'td .oe_currency_value:first:contains("150")',
                extra_trigger: 'td .oe_currency_value:last:contains("500")',
            },
            {
                content: 'Begin checkout process',
                trigger: '.btn-primary span',
                run: function(actions) {
                    actions.click('.btn-primary span');
                },
            },
            {
                content: 'Continue to payment page',
                trigger: 'h3:contains("Billing Address")',
                run: function(actions) {
                    actions.click('.btn-primary span');
                },
            },
            {
                content: 'Check that correct subtotals are shown on payment page',
                trigger: 'td .oe_currency_value:last:contains("500")',
                extra_trigger: 'td .oe_currency_value:first:contains("150")',
            },
        ]
    );
});
