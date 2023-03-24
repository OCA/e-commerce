odoo.define("website_sale_stock_list_preview.shop_stock", function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");
    var core = require("web.core");
    const {Markup} = require("web.utils");

    publicWidget.registry.WebsiteSaleStockListPreview = publicWidget.Widget.extend({
        selector: "#products_grid",
        xmlDependencies: [
            "/website_sale_stock/static/src/xml/website_sale_stock_product_availability.xml",
        ],
        events: {
            "click .btn.btn-primary.a-submit": "_onAddToCartClicked",
        },
        start: function () {
            return $.when.apply($, [
                this._super.apply(this, arguments),
                this.render_stock(),
            ]);
        },
        render_stock: function () {
            const $products = $(".o_wsale_product_grid_wrapper");
            this._render_stock($products);
        },
        _onAddToCartClicked: function (ev) {
            const $product = $(ev.currentTarget).closest(
                ".o_wsale_product_grid_wrapper"
            );
            this._render_stock($product, {button_cart_clicked: true});
        },
        _render_stock: function ($products, options) {
            const product_dic = {};
            $products.each(function () {
                product_dic[this.querySelector("a img").src.split("/")[6]] = this;
            });
            const product_ids = Object.keys(product_dic).map(Number);
            return this._rpc({
                route: "/sale/get_combination_info_stock_preview/",
                params: {product_template_ids: product_ids},
            }).then((products_qty) => {
                for (const product of products_qty) {
                    $(product_dic[product.product_template])
                        .find(".availability_message_" + product.product_template)
                        .remove();
                    product.free_qty -= product.cart_qty;
                    if (product.free_qty && options && options.button_cart_clicked) {
                        product.cart_qty++;
                        product.free_qty--;
                    }
                    $(product_dic[product.product_template])
                        .find(".product_price")
                        .append(
                            $(
                                core.qweb.render(
                                    "website_sale_stock.product_availability",
                                    {
                                        product_template: product.product_template,
                                        product_type: product.product_type,
                                        free_qty: product.free_qty,
                                        cart_qty: product.cart_qty,
                                        has_out_of_stock_message:
                                            $(product.out_of_stock_message).text() !==
                                            "",
                                        out_of_stock_message: Markup(
                                            product.out_of_stock_message
                                        ),
                                        allow_out_of_stock_order:
                                            product.allow_out_of_stock_order,
                                        show_availability: product.show_availability,
                                        available_threshold:
                                            product.available_threshold,
                                        uom_name: product.uom_name,
                                    }
                                )
                            ).get(0)
                        );
                    // With this code we active just the products that can be sold on website.
                    if (
                        product.free_qty <= 0 &&
                        !product.cart_qty &&
                        !product.allow_out_of_stock_order
                    ) {
                        $(product_dic[product.product_template])
                            .find(".fa-spinner")
                            .addClass("d-none");
                        $(product_dic[product.product_template])
                            .find(".fa-shopping-cart")
                            .removeClass("d-none");
                    } else {
                        $(product_dic[product.product_template])
                            .find(".fa-spinner")
                            .addClass("d-none");
                        $(product_dic[product.product_template])
                            .find(".fa-shopping-cart")
                            .removeClass("d-none");
                        $(product_dic[product.product_template])
                            .find(".fa-shopping-cart")
                            .parent()
                            .removeClass("disabled");
                    }
                }
            });
        },
    });
});
