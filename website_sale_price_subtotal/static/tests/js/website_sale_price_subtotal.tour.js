/* Copyright 2017 Specialty Medical Drugstore, LLC
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

odoo.define('website_sale_price_subtotal.tour', function (require) {
    "use strict";

    var tour = require('web_tour.tour');
    var base = require('web_editor.base');

    tour.register(
        'test_website_sale_price_subtotal',
        {
            url: '/shop/product/e-com07-ipad-mini-13',
            name: 'Test JS to check that the price corresponds to the quantity',
            test: true,
            wait_for: base.ready(),
        },
        [
            {
                content: 'Change the quantity to 2',
                trigger: '.css_quantity input',
                run: 'text 2',
            },
            {
                content: 'Check that the original price has been doubled',
                trigger: '.oe_currency_value:contains("640.00")',
            }
        ]
    );

    return {};

});
