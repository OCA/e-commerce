// Copyright 2020 Tecnativa - Alexandre Díaz
// License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
odoo.define("website_snippet_product_category.s_product_category", function (require) {
    "use strict";

    var core = require("web.core");
    var sAnimation = require("website.content.snippets.animation");

    var _t = core._t;


    sAnimation.registry.js_product_category = sAnimation.Class.extend({
        selector: ".js_product_category",

        /**
         * Asynchronous server side template rendering
         * @override
         */
        start: function () {
            var self = this;
            var template =
                this.$target.data("template") ||
                "website_snippet_product_category.s_product_category_items";
            // Prevent user edition
            this.$target.attr("contenteditable", "False");

            var def = this._rpc({
                route: "/website_sale/render_product_category",
                params: {
                    template: template,
                },
            })
                .then(
                    function (object_html) {
                        var $object_html = $(object_html);
                        var count = $object_html
                            .find("input[name='object_count']")
                            .val();
                        if (!count) {
                            self.$target.append(
                                $("<div/>").append(
                                    $("<div/>", {
                                        class:
                                            "alert alert-warning" +
                                            " alert-dismissible text-center",
                                        text: _t(
                                            "No categories were found. Make" +
                                            " sure you have categories" +
                                            " defined."
                                        ),
                                    })
                                )
                            );
                            return;
                        }

                        self.$target.html($object_html);
                    },
                    function () {
                        if (self.editableMode) {
                            self.$target.append(
                                $("<p/>", {
                                    class: "text-danger",
                                    text: _t(
                                        "An error occured with this product" +
                                        " categories block. If the problem" +
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
