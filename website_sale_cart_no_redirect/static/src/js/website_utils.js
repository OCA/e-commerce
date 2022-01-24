/* License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */
odoo.define("website_sale_cart_no_redirect.utils", function(require) {
    "use strict";

    const wUtils = require("website_sale.utils");

    const cartHandlerMixin = {
        getRedirectOption() {
            const html = document.documentElement;
            this.stayOnPageOption = html.dataset.add2cartRedirect !== "0";
        },
        getCartHandlerOptions(ev) {
            this.isBuyNow = ev.currentTarget.classList.contains("o_we_buy_now");
            let targetSelector =
                ev.currentTarget.dataset.animationSelector || "img.product_detail_img";

            if ($("#products_grid").length) {
                targetSelector = ev.currentTarget.dataset.animationSelector || "img";
            }
            this.$itemImgContainer = this.$(ev.currentTarget).closest(
                `:has(${targetSelector})`
            );
        },
        /**
         * Used to add product depending on stayOnPageOption value.
         */
        addToCart(params) {
            if (this.isBuyNow) {
                params.express = true;
            } else if (this.stayOnPageOption) {
                return this._addToCartInPage(params);
            }
            return wUtils.sendRequest("/shop/cart/update", params);
        },
        /**
         * @private
         */
        _addToCartInPage(params) {
            params.force_create = true;
            this._rpc({
                route: "/shop/cart/update_json",
                params: params,
            }).then(data => {
                wUtils.updateCartNavBar(data);
                wUtils.animateClone(
                    $("header .o_wsale_my_cart").first(),
                    this.$itemImgContainer,
                    25,
                    40
                );
            });
        },
    };
    return {
        cartHandlerMixin: cartHandlerMixin,
    };
});
