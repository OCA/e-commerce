odoo.define("website_sale_product_minimal_price.load", function (require) {
    "use strict";
    const ajax = require("web.ajax");
    const core = require("web.core");
    const field_utils = require("web.field_utils");
    const publicWidget = require("web.public.widget");
    const VariantMixin = require("sale.VariantMixin");
    const QWeb = core.qweb;
    const load_xml = ajax.loadXML(
        "/website_sale_product_minimal_price/static/src/xml/" +
            "website_sale_product_price_scale.xml",
        QWeb
    );

    VariantMixin._onChangeQtyWebsiteSale = function (ev, $parent, combination) {
        if (!this.isWebsite) {
            return;
        }
        ajax.jsonRpc("/sale/get_combination_info_pricelist_atributes", "call", {
            product_id: combination.product_id,
        }).then(function (vals) {
            const unit_prices = vals[0];
            const uom_name = vals[1];
            $(".temporal").remove();
            if (unit_prices.length > 0) {
                load_xml.then(function () {
                    const $form = $('form[action*="/shop/cart/update"]');
                    $form.append('<hr class="temporal"/>');
                    $form.append(
                        QWeb.render("website_sale_product_minimal_price.title", {
                            uom: uom_name,
                        })
                    );
                    // We define a limit of displayed columns as 4
                    const limit_col = 4;
                    let $div; // eslint-disable-line init-declarations
                    for (const i in unit_prices) {
                        if (unit_prices[i].price === 0) {
                            continue;
                        }
                        if (i % limit_col === 0) {
                            const id = i / limit_col;
                            $form.append(
                                '<div id="row_' + id + '" class="row temporal"></div>'
                            );
                            $div = $("#row_" + id);
                        }
                        let monetary_u = field_utils.format.monetary(
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
                    for (let i = 0; i < $div.length - 1; i++) {
                        $($div[i]).addClass("border-bottom");
                    }
                });
            }
        });
    };
    publicWidget.registry.WebsiteSale.include({
        /**
         * Add _onChangeQtyWebsiteSale to _onChangeCombination method.
         *
         * @override
         */
        _onChangeCombination: function () {
            VariantMixin._onChangeQtyWebsiteSale.apply(this, arguments);
            return this._super.apply(this, arguments);
        },
    });
    return VariantMixin;
});
