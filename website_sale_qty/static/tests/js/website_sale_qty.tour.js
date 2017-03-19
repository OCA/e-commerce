/**
*    Copyright 2016 LasLabs Inc.
*    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
**/

odoo.define('website_sale.tour', function(require) {
    'use strict';

    var tour = require('web_tour.tour');
    var base = require('web_editor.base');

    tour.register(
        'test_website_sale_qty',
        {
            url: '/shop/product/e-com07-ipad-mini-13',
            name: 'Test JS for price/quantity radio buttons on product page in website shop',
            test: true,
            wait_for: base.ready(),
        },
        [
            {
                content: 'Check that the radio corresponding to a quantity of 1 is selected on load',
                trigger: '.js-pqt-input[value="1"]:propChecked',
            },
            {
                content: 'Select the radio corresponding to a quantity of 5',
                trigger: '.js-pqt-input[value="5"]',
            },
            {
                content: 'Check that the main quantity input has been updated to 5',
                trigger: '.css_quantity input:propValue("5")',
            },
            {
                content: 'Change value of main quantity input to 6',
                trigger: '.css_quantity input[name=add_qty]',
                run: 'text 6',
            },
            {
                content: 'Check that none of the radios is selected anymore',
                trigger: '.js-pqt-input:not(:propChecked)',
            },
            {
                content: 'Change value of main quantity input to 5',
                trigger: '.css_quantity input[name=add_qty]',
                run: 'text 5',
            },
            {
                content: 'Check that the radio corresponding to a quantity of 5 is now selected',
                trigger: '.js-pqt-input[value="5"]:propChecked',
            },
            {
                content: 'Click button that decrements main quantity input',
                trigger: '.css_quantity a:even',
                run: 'click',
            },
            {
                content: 'Check that none of the radios is selected anymore',
                trigger: '.js-pqt-input:not(:propChecked)',
            },
            {
                content: 'Click button that increments main quantity input',
                trigger: '.css_quantity a:odd',
                run: 'click',
            },
            {
                content: 'Check that the radio corresponding to a quantity of 5 is now selected',
                trigger: '.js-pqt-input[value="5"]:propChecked',
            },
        ]
    );

    return {};

});