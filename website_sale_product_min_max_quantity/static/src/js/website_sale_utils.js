/*
 *   Copyright (c) 2023
 *   All rights reserved.
 */

odoo.define("website_sale_product_min_max_quantity.click", function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");

    publicWidget.registry.ProductMinMax = publicWidget.Widget.extend({
        selector: ".oe_website_sale",
        events: {
            "mousedown .js_delete_product": "_onClickDeleteProduct",
        },

        _onClickDeleteProduct: function (ev) {
            var $input = $(ev.currentTarget).closest("tr").find("input.js_quantity");
            $input.attr("min", 0);
            $input.attr("max", 10000);
        },
    });

    return publicWidget.registry.ProductMinMax;
});

odoo.define("website_sale_product_min_max_quantity.quantity", function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");

    publicWidget.registry.WebsiteSaleQuantity = publicWidget.Widget.extend({
        selector: ".oe_website_sale",
        events: {
            "change .quantity": "_onQuantityChange",
        },

        _onQuantityChange: function (ev) {
            var $input = $(ev.currentTarget);
            var minQty = parseFloat($input.attr("min"));
            var maxQty = parseFloat($input.attr("max"));
            if ($input.val() < minQty) {
                $input.val(minQty);
            }
            if ($input.val() > maxQty) {
                $input.val(maxQty);
            }
        },
    });

    return publicWidget.registry.WebsiteSaleQuantity;
});

odoo.define("website_sale_product_min_max_quantity.cart_quantity", function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");

    publicWidget.registry.WebsiteSaleCartQuantity = publicWidget.Widget.extend({
        selector: ".oe_website_sale",
        events: {
            "change .js_quantity": "_onQuantityChange",
        },

        _onQuantityChange: function (ev) {
            var $input = $(ev.currentTarget);
            var minQty = parseFloat($input.attr("min"));
            var maxQty = parseFloat($input.attr("max"));
            if ($input.val() < minQty) {
                $input.val(minQty);
            }
            if ($input.val() > maxQty) {
                $input.val(maxQty);
            }
        },
    });

    return publicWidget.registry.WebsiteSaleCartQuantity;
});

odoo.define("website_sale_product_min_max_quantity.utils", function (require) {
    "use strict";

    var wSaleUtils = require("website_sale.utils");
    var cartHandlerMixin = wSaleUtils.cartHandlerMixin;
    var core = require("web.core");
    var _t = core._t;

    cartHandlerMixin._addToCartInPage = function (params) {
        params.force_create = true;
        return this._rpc({
            route: "/shop/cart/update_json",
            params: params,
        }).then(async (data) => {
            if (data.warning === "maxquantity") {
                $("#add_to_cart").popover({
                    content: _t(
                        "The maximum purchase quantity has been exceeded.\nIt has been adjusted to the maximum purchase quantity."
                    ),
                    title: _t("ADVERTENCIA"),
                    placement: "right",
                    trigger: "focus",
                    html: true,
                });
                $("#add_to_cart").popover("show");
                setTimeout(function () {
                    $("#add_to_cart").popover("dispose");
                }, 5000);
            }
            sessionStorage.setItem("website_sale_cart_quantity", data.cart_quantity);
            if (
                data.cart_quantity &&
                data.cart_quantity !== parseInt($(".my_cart_quantity").text(), 2)
            ) {
                if ($("div[data-image_width]").data("image_width") !== "none") {
                    await wSaleUtils.animateClone(
                        $("header .o_wsale_my_cart").first(),
                        this.$itemImgContainer,
                        25,
                        40
                    );
                }
                wSaleUtils.updateCartNavBar(data);
            }
        });
    };
});
