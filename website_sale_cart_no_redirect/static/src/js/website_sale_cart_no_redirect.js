/* License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */
odoo.define("website_sale_cart_no_redirect.cart_", function(require) {
    "use strict";

    const publicWidget = require("web.public.widget");
    const wSaleCartUtils = require("website_sale_cart_no_redirect.utils");
    const cartHandlerMixin = wSaleCartUtils.cartHandlerMixin;

    publicWidget.registry.WebsiteSale = publicWidget.registry.WebsiteSale.extend(
        cartHandlerMixin,
        {
            /**
             * @override
             */
            start: function() {
                this.getRedirectOption();
                return this._super.apply(this, arguments);
            },
            /**
             * @override
             */
            _onClickAdd: function(ev) {
                if (!this.stayOnPageOption) {
                    return this._super.apply(this, arguments);
                }
                ev.preventDefault();
                this.getCartHandlerOptions(ev);
                return this._handleAdd($(ev.currentTarget).closest("form"));
            },
            /**
             * @override
             */
            _submitForm: function() {
                if (!this.stayOnPageOption) {
                    return this._super.apply(this, arguments);
                }
                if (this.optionalProductsModal && this.stayOnPageOption) {
                    this.optionalProductsModal._openedResolver();
                }
                const params = this.rootProduct;
                params.add_qty = params.quantity;

                params.product_custom_attribute_values = JSON.stringify(
                    params.product_custom_attribute_values
                );
                params.no_variant_attribute_values = JSON.stringify(
                    params.no_variant_attribute_values
                );
                this.addToCart(params);
            },
        }
    );
});
