// Copyright 2020 Tecnativa - Alexandre Díaz
// License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
odoo.define("website_snippet_carousel_product.s_product_carousel", function(require) {
    "use strict";

    const core = require("web.core");
    const sAnimation = require("website.content.snippets.animation");

    const _t = core._t;

    sAnimation.registry.js_product_carousel = sAnimation.Class.extend({
        selector: ".js_product_carousel",
        disabledInEditableMode: false,

        /**
         * @override
         */
        start: function() {
            const _this = this;
            const limit = Number(this.$target.attr("data-products-limit")) || 12;
            const domain = this.$target.attr("data-domain") || "[]";
            const products_per_slide =
                Number(this.$target.attr("data-products-per-slide")) || 4;
            let interval = Number(this.$target.attr("data-interval"));
            if (_.isNaN(interval)) {
                interval = 5000;
            }

            // Prevent user edition
            this.$target.attr("contenteditable", "false");

            // Loading Indicator
            this.$target.html(
                $("<div/>", {class: "text-center p-5 my-5 text-muted"}).append(
                    $("<i/>", {
                        class: "fa fa-circle-o-notch fa-spin fa-3x fa-fwg mr-1",
                    })
                )
            );

            const def = this._rpc({
                route: "/website/render_product_carousel",
                params: {
                    limit: limit,
                    domain: JSON.parse(domain),
                    products_per_slide: products_per_slide,
                },
            }).then(
                function(object_html) {
                    const $object_html = $(object_html);
                    $object_html.find(".oe_product").removeClass("oe_image_full");
                    const count = $object_html
                        .find("input[name='product_count']")
                        .val();
                    if (!count) {
                        _this.$target.append(
                            $("<div/>", {class: "col-md-6 offset-md-3"}).append(
                                $("<div/>", {
                                    class:
                                        "alert alert-warning" +
                                        " alert-dismissible text-center",
                                    text: _t(
                                        "No products was found." +
                                            " Make sure you have products" +
                                            " published on the website."
                                    ),
                                })
                            )
                        );
                        return;
                    }

                    _this.$target.html($object_html);
                    _this.$target.find(".carousel").carousel({
                        interval: interval,
                    });
                    // Initialize 'animations' for the product card.
                    // This is necessary because the snippet is asynchonously
                    // rendered on the server.
                    _this.trigger_up("widgets_start_request", {
                        $target: _this.$target.find(".oe_website_sale"),
                    });
                },
                function() {
                    if (_this.editableMode) {
                        _this.$target.append(
                            $("<p/>", {
                                class: "text-danger",
                                text: _t(
                                    "An error occured with this product" +
                                        " carousel block. If the problem" +
                                        " persists, please consider deleting" +
                                        " it and adding a new one"
                                ),
                            })
                        );
                    }
                }
            );
            return $.when(this._super.apply(this, arguments), def);
        },
        /**
         * @override
         */
        destroy: function() {
            this.$target.empty();
            this._super.apply(this, arguments);
        },
    });
});
