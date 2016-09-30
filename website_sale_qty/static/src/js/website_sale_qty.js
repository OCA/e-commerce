/**
*    Copyright 2016 LasLabs Inc.
*    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
**/

odoo.define('website_sale_qty', function(require) {
    'use strict';

    var base = require('web_editor.base');
    var $ = require('$');
    base.ready().done(function() {
        var radios = $('.js-pqt-input');

        if (radios.length > 0) {
            var _ = require('_');
            var radioMap = {};
            _.each(radios, function(element) {
                var $element = $(element);
                radioMap[$element.val()] = $element;
            });
            var quantityInput = $('.css_quantity input');
            var quantityToggles = $('.css_quantity a');

            // If present, this input should be selected by default
            if (1 in radioMap) {
                radioMap[1].prop('checked', true);
            }

            radios.click(function(event) {
                var newValue = $(event.currentTarget).val();
                quantityInput.val(newValue).trigger('change');
            });

            var updateRadios = function() {
                radios.prop('checked', false);

                var newValue = quantityInput.val();
                if (newValue in radioMap) {
                    radioMap[newValue].prop('checked', true);
                }
            };

            quantityInput.on('input', updateRadios);
            quantityToggles.click(function() {
                // This allows website_sale.website_sale to update the input first
                setTimeout(updateRadios, 0);
            });
        }
    });
});
