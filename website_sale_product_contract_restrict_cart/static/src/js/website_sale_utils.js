/* Copyright 2023 Onestein - Anjeel Haria
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
odoo.define(
    "website_sale_product_contract_cart.website_sale_utils",
    function (require) {
        "use strict";

        const wsUtils = require("website_sale.utils");
        const cartHandlerMixin = {
            _addToCartInPage(params) {
                params.force_create = true;
                return this._rpc({
                    route: "/shop/cart/update_json",
                    params: params,
                }).then(async (data) => {
                    sessionStorage.setItem(
                        "website_sale_cart_quantity",
                        data.cart_quantity
                    );
                    if (
                        data.cart_quantity &&
                        data.cart_quantity !== parseInt($(".my_cart_quantity").text())
                    ) {
                        if ($("div[data-image_width]").data("image_width") !== "none") {
                            await wsUtils.animateClone(
                                $("header .o_wsale_my_cart").first(),
                                this.$itemImgContainer,
                                25,
                                40
                            );
                        }
                        wsUtils.updateCartNavBar(data);
                    }
                    if (data.warning) {
                        wsUtils.showWarning(data.warning);
                    }
                });
            },
        };

        wsUtils.cartHandlerMixin = {
            ...wsUtils.cartHandlerMixin,
            ...cartHandlerMixin,
        };
    }
);
