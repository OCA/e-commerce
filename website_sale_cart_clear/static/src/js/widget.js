odoo.define("website_sale_cart_clear.widget", function (require) {
    "use strict";

    var websiteSaleWidgets = require("website_sale.website_sale");

    websiteSaleWidgets.websiteSaleCart.include({
        events: _.extend(websiteSaleWidgets.websiteSaleCart.prototype.events, {
            "click .js_clear_cart": "_onClickClearCart",
        }),

        _onClickClearCart() {
            return this._rpc({
                route: "/shop/cart/clear",
            }).then(() => {
                location.reload();
            });
        },
    });
});
