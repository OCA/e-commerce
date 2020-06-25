odoo.define("website_sale_product_minimal_price.shop_min_price", function(require) {
    "use strict";

    const publicWidget = require("web.public.widget");
    const core = require("web.core");
    const field_utils = require("web.field_utils");

    publicWidget.registry.WebsiteSaleProductMinimalPrice = publicWidget.Widget.extend({
        selector: "#products_grid",
        xmlDependencies: [
            "/website_sale_product_minimal_price/static/src/xml/website_sale_product_minimal_price.xml",
        ],

        start: function() {
            return Promise.all([
                this._super.apply(this, arguments),
                this.render_price(),
            ]);
        },
        render_price: async function() {
            const $products = $(".o_wsale_product_grid_wrapper");
            const product_dic = {};
            $products.each(function() {
                product_dic[this.querySelector("a img").src.split("/")[6]] = this;
            });
            const product_ids = Object.keys(product_dic).map(Number);
            const products_min_price = await this._rpc({
                route: "/sale/get_combination_info_minimal_price/",
                params: {product_template_ids: product_ids},
            });

            for (const product of products_min_price) {
                if (!product.distinct_prices) {
                    continue;
                }
                $(product_dic[product.id])
                    .find(".product_price")
                    .prepend(
                        $(
                            core.qweb.render(
                                "website_sale_product_minimal_price.from_view"
                            )
                        ).get(0)
                    );
                $(product_dic[product.id])
                    .find(".product_price .oe_currency_value")
                    .replaceWith(
                        $(
                            core.qweb.render(
                                "website_sale_product_minimal_price.product_minimal_price",
                                {
                                    price: this.widgetMonetary(product.price),
                                }
                            )
                        ).get(0)
                    );
            }
            return products_min_price;
        },
        widgetMonetary: function(value) {
            return field_utils.format.monetary(value);
        },
    });
});
