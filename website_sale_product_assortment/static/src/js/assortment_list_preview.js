odoo.define("website_sale_product_assortment.assortment_preview", function (require) {
    "use strict";

    const publicWidget = require("web.public.widget");
    const core = require("web.core");

    publicWidget.registry.WebsiteSaleProductAssortment = publicWidget.Widget.extend({
        selector: "#products_grid",
        xmlDependencies: [
            "/website_sale_product_assortment/static/src/xml/website_sale_product_assortment.xml",
        ],

        start: function () {
            return $.when.apply($, [
                this._super.apply(this, arguments),
                this.render_assortments(),
            ]);
        },
        render_assortments: function () {
            const $products = $(".o_wsale_product_grid_wrapper");
            const product_dic = {};
            $products.each(function () {
                product_dic[this.querySelector("a img").src.split("/")[6]] = this;
            });
            const product_ids = Object.keys(product_dic).map(Number);
            return this._rpc({
                route: "/sale/get_info_assortment_preview",
                params: {product_template_ids: product_ids},
            }).then((product_values) => {
                for (const product of product_values) {
                    this.render_product_assortment(product_dic[product.id], product);
                }
            });
        },
        render_product_assortment: function (product_info, product) {
            $(product_info)
                .find(".product_price")
                .append(
                    $(
                        core.qweb.render(
                            "website_sale_product_assortment.product_availability",
                            {
                                message_unavailable: product.message_unavailable,
                                product_template_id: product.id,
                            }
                        )
                    ).get(0)
                );

            $(product_info).find(".fa-shopping-cart").parent().addClass("disabled");
        },
    });
});
