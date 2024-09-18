odoo.define("website_sale_float_cart_qty.float_qty", function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");
    var wSaleUtils = require("website_sale.utils");
    var core = require("web.core");
    require("website_sale.website_sale");

    publicWidget.registry.WebsiteSale.include({
        /**
         * Override the _changeCartQuantity method of WebsiteSale
         * @param {jQuery} $input - The jQuery object representing the input field.
         * @param {Number} value - The new value of the input field.
         * @param {Array} $dom_optional - Array of DOM elements.
         * @param {Number} line_id - The line ID associated with the cart line.
         * @param {Array} productIDs - Array of product IDs.
         */

        _changeCartQuantity: function (
            $input,
            value,
            $dom_optional,
            line_id,
            productIDs
        ) {
            _.each($dom_optional, function (elem) {
                $(elem).find(".js_quantity").text(value);
                productIDs.push(
                    $(elem).find("span[data-product-id]").data("product-id")
                );
            });
            $input.data("update_change", true);

            $input.val($input.val().replace(",", "."));

            this._rpc({
                route: "/shop/cart/update_json",
                params: {
                    line_id: line_id,
                    product_id: parseInt($input.data("product-id"), 10),
                    set_qty: value,
                },
            }).then(function (data) {
                $input.data("update_change", false);
                var check_value = parseFloat($input.val() || 0, 10);
                if (isNaN(check_value)) {
                    check_value = 1;
                }
                if (value !== check_value) {
                    $input.trigger("change");
                    return;
                }
                sessionStorage.setItem(
                    "website_sale_cart_quantity",
                    data.cart_quantity
                );
                if (!data.cart_quantity) {
                    return (window.location = "/shop/cart");
                }
                $input.val(data.quantity);
                $(".js_quantity[data-line-id=" + line_id + "]")
                    .val(data.quantity)
                    .text(data.quantity);

                wSaleUtils.updateCartNavBar(data);
                wSaleUtils.showWarning(data.warning);
                // Propagating the change to the express checkout forms
                core.bus.trigger("cart_amount_changed", data.amount, data.minor_amount);
            });
        },

        _onChangeCartQuantity: function (ev) {
            var $input = $(ev.currentTarget);
            if ($input.data("update_change")) {
                return;
            }
            var value = $input.val().replace(",", ".");
            value = parseFloat(value);
            var $dom = $input.closest("tr");
            var $dom_optional = $dom.nextUntil(":not(.optional_product.info)");
            var line_id = parseInt($input.data("line-id"), 10);
            var productIDs = [parseInt($input.data("product-id"), 10)];
            this._changeCartQuantity($input, value, $dom_optional, line_id, productIDs);
        },
    });
});
