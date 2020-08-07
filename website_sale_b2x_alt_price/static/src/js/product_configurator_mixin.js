/* Copyright 2020 Jairo Llopis - Tecnativa
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

odoo.define("website_sale_b2x_alt_price", function (require) {
    "use strict";

    var ProductConfiguratorMixin = require("sale.ProductConfiguratorMixin");
    var animation = require("website.content.snippets.animation");

    /**
     * Change alt prices when picking a product configurator combination.
     *
     * Addition to `ProductConfiguratorMixin._onChangeCombination`.
     *
     * This behavior is only applied for the web shop (and not on the SO form)
     * and only for the main product.
     *
     * @see onChangeVariant
     *
     * @private
     * @param {MouseEvent} _ev
     * @param {$.Element} $parent
     * @param {Object} combination
     */
    ProductConfiguratorMixin._onChangeCombinationAltPrices = function (
        _ev,
        $parent,
        combination
    ) {
        // Write new alt prices
        $parent
            .find(".js_alt_price .oe_currency_value")
            .text(this._priceToStr(combination.alt_price));
        $parent
            .find(".js_alt_list_price")
            .toggleClass("d-none", !combination.has_discounted_price)
            .find(".oe_currency_value")
            .text(this._priceToStr(combination.alt_list_price));
    };

    animation.registry.WebsiteSale.include({
        /**
         * Add alt price onchange to the regular _onChangeCombination method.
         *
         * @override
         */
        _onChangeCombination: function () {
            ProductConfiguratorMixin._onChangeCombinationAltPrices.apply(
                this,
                arguments
            );
            return this._super.apply(this, arguments);
        },
    });

    return ProductConfiguratorMixin;
});
