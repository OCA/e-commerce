odoo.define("website_sale_stock_list_preview.shop_stock", function(require) {
    "use strict";

    var publicWidget = require("web.public.widget");
    var core = require("web.core");

    publicWidget.registry.WebsiteSaleStockListPreview = publicWidget.Widget.extend({
        selector: "#products_grid",
        xmlDependencies: [
            "/website_sale_stock/static/src/xml/website_sale_stock_product_availability.xml",
        ],

        start: function() {
            return $.when.apply($, [
                this._super.apply(this, arguments),
                this.render_stock(),
            ]);
        },
        render_stock: function() {
            const $products = $(".o_wsale_product_grid_wrapper");
            const product_dic = {};
            $products.each(function() {
                product_dic[this.querySelector("a img").src.split("/")[6]] = this;
            });
            const product_ids = Object.keys(product_dic).map(Number);
            return this._rpc({
                route: "/sale/get_combination_info_stock_preview/",
                params: {product_template_ids: product_ids},
            }).then(products_qty => {
                for (const product of products_qty) {
                    $(product_dic[product.id])
                        .find(".product_price")
                        .append(
                            $(
                                core.qweb.render(
                                    "website_sale_stock.product_availability",
                                    {
                                        virtual_available: product.virtual_available,
                                        virtual_available_formatted:
                                            product.virtual_available_formatted,
                                        inventory_availability:
                                            product.inventory_availability,
                                        available_threshold:
                                            product.available_threshold,
                                        custom_message: product.custom_message,
                                        product_template: product.id,
                                        product_type: product.type,
                                        uom_name: product.uom_name,
                                    }
                                )
                            ).get(0)
                        );
                    // With this code we active just the products that can be sold on website.
                    if (
                        product.virtual_available <= 0 &&
                        (product.inventory_availability == "always" ||
                            product.inventory_availability == "threshold")
                    ) {
                        $(product_dic[product.id])
                            .find(".fa-spinner")
                            .addClass("d-none");
                        $(product_dic[product.id])
                            .find(".fa-shopping-cart")
                            .removeClass("d-none");
                    } else {
                        $(product_dic[product.id])
                            .find(".fa-spinner")
                            .addClass("d-none");
                        $(product_dic[product.id])
                            .find(".fa-shopping-cart")
                            .removeClass("d-none");
                        $(product_dic[product.id])
                            .find(".fa-shopping-cart")
                            .parent()
                            .removeClass("disabled");
                    }
                }
            });
        },
    });
});
