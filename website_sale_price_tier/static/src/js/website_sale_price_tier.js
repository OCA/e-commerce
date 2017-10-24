/* Copyright 2016-2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html) */

odoo.define('website_sale_price_tier', function(require) {
    'use strict';

    var base = require('web_editor.base');
    base.ready().done(function() {
        var $radios = $('.js-pqt-input');

        if ($radios.length > 0) {
            var radioMap = {};
            _.each($radios, function(element) {
                var $element = $(element);
                radioMap[$element.val()] = $element;
            });
            var $quantityInput = $('.css_quantity input');
            var $quantityToggles = $('.css_quantity a');

            $radios.click(function(event) {
                var newValue = $(event.currentTarget).val();
                $quantityInput.val(newValue).trigger('change');
            });

            var updateRadios = function() {
                $radios.prop('checked', false);

                var newValue = $quantityInput.val();
                if (newValue in radioMap) {
                    radioMap[newValue].prop('checked', true);
                }
            };

            // Lowest tier should be selected by default unless quantity has
            // already been modified (e.g. by website_sale_select_qty)
            if ($quantityInput.val() === '1') {
                $radios.first().click();
            } else {
                updateRadios();
            }

            $quantityInput.on('input', updateRadios);
            $quantityToggles.click(function() {
                // setTimeout puts the callback at the end of the event queue
                // for this click event so that website_sale.website_sale can
                // first respond to the click by updating the input value
                setTimeout(updateRadios, 0);
            });
        }
    });
});
