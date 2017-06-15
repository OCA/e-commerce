/* Copyright 2017 LasLabs Inc.
 * License LGPL-3 or later (http://www.gnu.org/licenses/lgpl.html) */

odoo.define('website_sale_price_subtotal', function(require) {
    'use strict';

    var base = require('web_editor.base');
    base.ready().done(function() {
        var $quantityInput = $('input[name="add_qty"]');
        var $priceStore = $('ul[data-attribute_value_ids]');

        if ($quantityInput.length > 0 && $priceStore.length > 0) {
            var basePrices = $priceStore.data('attribute_value_ids');
            var basePublicPrices = basePrices.map(function(element) {
                return element[3];
            });

            var pricesToSubtotals = function() {
                var quantity = parseInt($quantityInput.val(), 10);
                var currentPrices = $priceStore.data('attribute_value_ids');
                for(var i = 0; i < currentPrices.length; i++) {
                    currentPrices[i][2] *= quantity;
                    currentPrices[i][3] = basePublicPrices[i] * quantity;
                }
                $priceStore.data(
                    'data-attribute_value_ids',
                    JSON.stringify(currentPrices)
                );

                // Signal that $priceStore has new values to display
                $priceStore.change();
            };
            // Run logic immediately in case quantity is not 1 from the start
            pricesToSubtotals();

            $quantityInput.change(function() {
                // Quantity has changed so next $priceStore change will have
                // fresh prices from server
                $priceStore.one('change', function() {
                    // Add this to end of event queue so that DOM updates
                    // triggered by current event can go through before
                    // pricesToSubtotals starts its own round of updates
                    setTimeout(pricesToSubtotals, 0);
                });
            });
        }
    });
});
