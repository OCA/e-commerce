// Copyright 2020 Tecnativa - Alexandre Díaz
// License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
odoo.define("website_snippet_carousel_product.s_product_carousel", function (require) {
    "use strict";

    var core = require("web.core");
    var sAnimation = require("website.content.snippets.animation");

    var _t = core._t;

    sAnimation.registry.js_product_carousel = sAnimation.Class.extend({
        selector: ".js_product_carousel",

        /**
         * @override
         */
        start: function () {
            var self = this;
            var limit = Number(this.$target.attr("data-products-limit")) || 12;
            var domain = this.$target.attr("data-domain") || "[]";
            var products_per_slide =
                Number(this.$target.attr("data-products-per-slide")) || 4;
            var interval = Number(this.$target.attr("data-interval"));
            if (_.isNaN(interval)) {
                interval = 5000;
            }

            // Prevent user edition
            this.$target.attr("contenteditable", "False");

            // Loading Indicator
            this.$target.html(
                $("<div/>", {class: "text-center p-5 my-5 text-muted"})
                .append($("<i/>", {
                    class: "fa fa-circle-o-notch fa-spin fa-3x fa-fwg mr-1"
                }))
            );

            var def = this._rpc({
                route: "/website/render_product_carousel",
                params: {
                    limit: limit,
                    domain: JSON.parse(domain),
                    products_per_slide: products_per_slide,
                },
            })
                .then(
                    function (object_html) {
                        var $object_html = $(object_html);
                        var count = $object_html
                            .find("input[name='product_count']")
                            .val();
                        if (!count) {
                            self.$target.append(
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

                        self.$target.html($object_html);
                        self.$target.find('.carousel').carousel({
                            interval: interval,
                        });
                        // Initialize 'animations' for the product card.
                        // This is necessary because the snippet is asynchonously
                        // rendered on the server.
                        self.trigger_up('animation_start_demand', {
                            $target: self.$target.find('.oe_website_sale'),
                        });
                    },
                    function () {
                        if (self.editableMode) {
                            self.$target.append(
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
        destroy: function () {
            this.$target.empty();
            this._super.apply(this, arguments);
        },
    });
});
