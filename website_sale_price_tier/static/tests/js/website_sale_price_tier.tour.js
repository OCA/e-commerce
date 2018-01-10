/* Copyright 2016-2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html) */

odoo.define('website_sale_price_tier.tour', function(require) {
    'use strict';

    var tour = require('web_tour.tour');
    var _t = require('web.core')._t;
    var base = require('web_editor.base');

    tour.register(
        'website_sale_price_tier',
        {
            test: true,
            name: _t('Test price/quantity radio buttons on product page in website shop'),
            url: '/shop',
            wait_for: base.ready(),
        },
        [
            {
                content: 'Search for "Price Tiers" to find demo product',
                trigger: 'input[name="search"]',
                run: function(actions) {
                    $('input[name="search"]').val('Price Tiers');
                    actions.click('.oe_search_button');
                },
            },
            {
                content: 'Check that lowest quantity tier is showing in search view',
                trigger: 'div.product_price > strong',
                run: function(actions) {
                    var $tierInfo = $('div.product_price > strong');
                    if ($tierInfo.text().indexOf('640') === -1) {
                        tour._consume_tour(
                            tour.running_tour,
                            'The lowest quantity tier is not showing in the search view'
                        );
                    }
                },
            },
            {
                content: 'Open product page for demo product',
                trigger: 'a:contains("Price Tiers - Demo Product")',
                run: function(actions) {
                    actions.click('a:contains("Price Tiers - Demo Product")');
                },
            },
            {
                content: 'Check that radio for lowest quantity tier is selected by default',
                trigger: '.js-pqt-input',
                run: function() {
                    var $radio = $('li:first-child input.js-pqt-input');
                    if (!$radio.is(':checked')) {
                        tour._consume_tour(
                            tour.running_tour,
                            'The radio button for the lowest quantity tier' +
                            ' is not selected by default'
                        );
                    }
                },
            },
            {
                content: 'Check that main quantity input matches radio selected by default',
                trigger: '.js-pqt-input',
                run: function() {
                    var $quantityInput = $('.css_quantity input');
                    if ($quantityInput.val() !== '2') {
                        tour._consume_tour(
                            tour.running_tour,
                            'The main quantity input does not match the' +
                            ' radio button that was selected by default'
                        );
                    }
                },
            },

            {
                content: 'Select the radio corresponding to a quantity of 5',
                trigger: '.js-pqt-input[value="5"]',
                run: function(actions) {
                    actions.click('.js-pqt-input[value="5"]');
                },
            },
            {
                content: 'Check that main quantity input has been updated to 5',
                trigger: '.js-pqt-input[value="5"]',
                run: function() {
                    var $quantityInput = $('.css_quantity input');
                    if ($quantityInput.val() !== '5') {
                        tour._consume_tour(
                            tour.running_tour,
                            'Selecting a radio button is not correctly' +
                            ' changing the main quantity input'
                        );
                    }
                },
            },

            {
                content: 'Change value of main quantity input to 6',
                trigger: '.css_quantity input',
                run: function() {
                    // Input event should be fired to properly replicate user action
                    $('.css_quantity input').val(6).trigger('input');
                },
            },
            {
                content: 'Check that none of the radios are selected anymore',
                trigger: '.js-pqt-input',
                run: function() {
                    var $radios = $('.js-pqt-input');
                    if ($radios.is(':checked')) {
                        tour._consume_tour(
                            tour.running_tour,
                            'A change to the main quantity input is not' +
                            'correctly clearing the selected radio buttons'
                        );
                    }
                },
            },

            {
                content: 'Change value of main quantity input to 5',
                trigger: '.css_quantity input',
                run: function() {
                    // Input event should be fired to properly replicate user action
                    $('.css_quantity input').val(5).trigger('input');
                },
            },
            {
                content: 'Check that radio corresponding to a quantity of 5 is now selected',
                trigger: '.js-pqt-input[value="5"]',
                run: function() {
                    var $radio = $('.js-pqt-input[value="5"]');
                    if (!$radio.is(':checked')) {
                        tour._consume_tour(
                            tour.running_tour,
                            'A change to the main quantity input is not' +
                            ' causing the corresponding radio to be selected'
                        );
                    }
                },
            },

            {
                content: 'Click button that increments main quantity input',
                trigger: '.css_quantity a:nth-of-type(2)',
                run: function(actions) {
                    actions.click('.css_quantity a:nth-of-type(2)');
                }
            },
            {
                content: 'Check that none of the radios are selected anymore',
                trigger: '.js-pqt-input',
                run: function() {
                    var $radios = $('.js-pqt-input');
                    if ($radios.is(':checked')) {
                        tour._consume_tour(
                            tour.running_tour,
                            'A quantity change via the plus button is not' +
                            ' correctly clearing the selected radio buttons'
                        );
                    }
                },
            },

            {
                content: 'Click button that decrements main quantity input',
                trigger: '.css_quantity a:nth-of-type(1)',
                run: function(actions) {
                    actions.click('.css_quantity a:nth-of-type(1)');
                }
            },
            {
                content: 'Check that the radio corresponding to a quantity of 5 is now selected',
                trigger: '.js-pqt-input[value="5"]',
                run: function() {
                    var $radio = $('.js-pqt-input[value="5"]');
                    if (!$radio.is(':checked')) {
                        tour._consume_tour(
                            tour.running_tour,
                            'A quantity change via the minus button is not' +
                            ' causing the corresponding radio to be selected'
                        );
                    }
                },
            },
        ]
    );
});
