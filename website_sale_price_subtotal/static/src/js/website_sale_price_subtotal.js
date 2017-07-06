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
            var priorWebPrices = _.map(Array(basePrices.length), function() {
                return 0;
            });
            var priorQuantity = 0;

            var pricesToSubtotals = function() {
                var currentQuantity = parseInt($quantityInput.val(), 10);
                var currentPrices = $priceStore.data('attribute_value_ids');
                var changing = false;

                if (currentQuantity !== priorQuantity) {
                    for(var j = 0; j < currentPrices.length; j++) {
                        currentPrices[j][2] *= currentQuantity;
                        priorWebPrices[j] = currentPrices[j][2];
                        currentPrices[j][3] = basePublicPrices[j] * currentQuantity;
                    }
                    priorQuantity = currentQuantity;
                    changing = true;
                } else if (currentPrices[0][2] !== priorWebPrices[0]) {
                    for(var k = 0; k < currentPrices.length; k++) {
                        currentPrices[k][2] *= currentQuantity;
                        priorWebPrices[k] = currentPrices[k][2];
                    }
                    changing = true;
                }

                if (changing) {
                    $priceStore.data(
                        'data-attribute_value_ids',
                        JSON.stringify(currentPrices)
                    );

                    // Signal that $priceStore has new values to display
                    $priceStore.change();
                }
            };
            // Run logic immediately in case quantity is not 1 from the start
            pricesToSubtotals();

            $priceStore.change(function() {
                // Add this to end of event queue so that DOM updates
                // triggered by priceStore update can go through before
                // pricesToSubtotals starts its own round of updates
                setTimeout(pricesToSubtotals, 0);
            });
        }
    });
});
