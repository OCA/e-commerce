odoo.define("website_sale_product_minimal_price.load", function (require) {
    "use strict";
    var ajax = require("web.ajax");
    var core = require("web.core");
    var field_utils = require("web.field_utils");
    var ProductConfiguratorMixin = require(
        "website_sale_stock.ProductConfiguratorMixin");
    var QWeb = core.qweb;
    var load_xml = ajax.loadXML(
        "/website_sale_product_minimal_price/static/src/xml/" +
            "website_sale_product_minimal_price.xml",
        QWeb
    );

    // Save original method
    var _onChangeCombinationStock =
        ProductConfiguratorMixin._onChangeCombinationStock;
    ProductConfiguratorMixin._onChangeCombinationStock = function (
        ev,
        $parent,
        combination
    ) {
        var self = this;
        var args = arguments;
        if (!this.isWebsite) {
            return;
        }
        ajax.jsonRpc("/sale/get_combination_info_pricelist_atributes", "call", {
            product_id: combination.product_id,
            actual_qty: $(".quantity").val(),
        }).then(function (unit_prices) {
            $(".temporal").remove();
            if (unit_prices.length > 0) {
                load_xml.then(function () {
                    var $form = $('form[action*="/shop/cart/update"]');
                    $form.append('<hr class="temporal"/>');
                    $form.append(
                        QWeb.render(
                            "website_sale_product_minimal_price.title",
                            {
                                uom: combination.uom_name,
                            }
                        )
                    );
                    // We define a limit of displayed columns as 4
                    const limit_col = 4;
                    var $div = undefined;
                    for (var i in unit_prices) {
                        if (unit_prices[i].price === 0) {
                            continue;
                        }
                        if (i % limit_col === 0) {
                            var id = i/limit_col;
                            $form.append('<div id="row_'+ id +'" class="row temporal"></div>');
                            $div = $('#row_' + id);
                        }
                        var monetary_u = field_utils.format.monetary(
                            unit_prices[i].price,
                            {},
                            {currency: unit_prices[i].currency}
                        );
                        monetary_u = monetary_u.replace("&nbsp;", " ");
                        $div.append(
                            QWeb.render(
                                "website_sale_product_minimal_price.pricelist",
                                {
                                    quantity: unit_prices[i].min_qty,
                                    price: monetary_u,
                                }
                            )
                        );
                    }
                    $div = $('div[id*="row_"]');
                    for (var i = 0; i < $div.length - 1; i++) {
                        $($div[i]).addClass('border-bottom');
                    }
                });
            } else {
                _onChangeCombinationStock.apply(self, args);
            }
        });
    };
    return ProductConfiguratorMixin;
});
