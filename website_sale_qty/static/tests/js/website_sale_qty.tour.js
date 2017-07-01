/**
*    Copyright 2016 LasLabs Inc.
*    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
**/

odoo.define('website_sale.tour', function(require) {
    'use strict';

    var tour = require('web.Tour');
    var _t = require('web.core')._t;

    tour.register({
        id: 'test_website_sale_qty',
        name: _t('Test JS for price/quantity radio buttons on product page in website shop'),
        path: '/shop/product/ipad-mini-9',
        mode: 'test',
        steps: [
            {
                title: 'Check that the radio corresponding to a quantity of 1 is selected on load',
                onload: function() {
                    var radio = $('.js-pqt-input[value="1"]');
                    if (!radio.is(':checked')) {
                        tour.error(this, 'The radio for a qty of 1 should be selected');
                    }
                },
            },

            {
                title: 'Select the radio corresponding to a quantity of 5',
                element: '.js-pqt-input[value="5"]',
            },
            {
                title: 'Check that the main quantity input has been updated to 5',
                onload: function() {
                    var quantityInput = $('.css_quantity input');
                    if (quantityInput.val() != 5) {
                        tour.error(this, "The main quantity input should have a value of 5");
                    }
                },
            },

            {
                title: 'Change value of main quantity input to 6',
                onload: function() {
                    // Input event should be fired to properly replicate user action
                    $('.css_quantity input').val(6).trigger('input');
                },
            },
            {
                title: 'Check that none of the radios are selected anymore',
                onload: function() {
                    var radios = $('.js-pqt-input');
                    if (radios.is(':checked')) {
                        tour.error(this, 'No radios should be selected at this point');
                    }
                },
            },

            {
                title: 'Change value of main quantity input to 5',
                onload: function() {
                    // Input event should be fired to properly replicate user action
                    $('.css_quantity input').val(5).trigger('input');
                },
            },
            {
                title: 'Check that the radio corresponding to a quantity of 5 is now selected',
                onload: function() {
                    var radio = $('.js-pqt-input[value="5"]');
                    if (!radio.is(':checked')) {
                        tour.error(this, 'The radio for a qty of 5 should be selected');
                    }
                },
            },

            {
                title: 'Click button that increments main quantity input',
                element: '.css_quantity a:nth-of-type(2)',
            },
            {
                title: 'Check that none of the radios are selected anymore',
                onload: function() {
                    var radios = $('.js-pqt-input');
                    if (radios.is(':checked')) {
                        tour.error(this, 'No radios should be selected at this point');
                    }
                },
            },
            
            {
                title: 'Click button that decrements main quantity input',
                element: '.css_quantity a:nth-of-type(1)',
            },
            {
                title: 'Check that the radio corresponding to a quantity of 5 is now selected',
                onload: function() {
                    var radio = $('.js-pqt-input[value="5"]');
                    if (!radio.is(':checked')) {
                        tour.error(this, 'The radio for a qty of 5 should be selected');
                    }
                },
            },
        ],
    });
});
