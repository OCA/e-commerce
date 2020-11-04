// Copyright 2020 Tecnativa - Alexandre Díaz
// License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
odoo.define("website_snippet_carousel_product.snippet_options", function (require) {
    "use strict";

    var core = require("web.core");
    var options = require("web_editor.snippets.options");
    var wUtils = require("website.utils");

    var _t = core._t;

    options.registry.js_product_carousel = options.Class.extend({
        popup_template_id: "editor_new_product_carousel_domain",
        popup_title: _t("Add a products carousel"),

        /**
         * @override
         */
        _onLinkClick: function (ev) {
            // Get the selected menu item
            var $elm = $(ev.target);
            if ($elm.is(".s_carousel_set_domain")) {
                this.select_domain();
            } else if ($elm.is("[data-products-per-slide]")) {
                this.$target.attr(
                    "data-products-per-slide",
                    $elm.attr("data-products-per-slide")
                );
                this._refreshAnimations();
            } else if ($elm.is("[data-products-limit]")) {
                this.$target.attr(
                    "data-products-limit",
                    $elm.attr("data-products-limit")
                );
                this._refreshAnimations();
            } else if ($elm.is("[data-interval]")) {
                this.$target.attr(
                    "data-interval",
                    $elm.attr("data-interval")
                );
                this._refreshAnimations();
            }
            return this._super.apply(this, arguments);
        },

        /**
         * @override
         */
        onBuilt: function () {
            this._super();
            this.select_domain();
        },

        /**
         * @override
         */
        _setActive: function () {
            var self = this;
            this._super.apply(this, arguments);
            // Active 'Limit' option
            this.$el
                .find("[data-products-limit]")
                .addBack("[data-products-limit]")
                .removeClass("active")
                .filter(function () {
                    var limit = $(this).attr("data-products-limit");
                    var old_limit =
                        self.$target.attr("data-products-limit") || '12';
                    return old_limit === limit;
                })
                .addClass("active");
            // Active 'Show' option
            this.$el
                .find("[data-products-per-slide]")
                .addBack("[data-products-per-slide]")
                .removeClass("active")
                .filter(function () {
                    var pps = $(this).attr("data-products-per-slide");
                    var old_pps =
                        self.$target.attr("data-products-per-slide") || '4';
                    return old_pps === pps;
                })
                .addClass("active");
            // Active 'Interval' option
            this.$el
                .find("[data-interval]")
                .addBack("[data-interval]")
                .removeClass("active")
                .filter(function () {
                    var interval = $(this).attr("data-interval");
                    var old_interval =
                        self.$target.attr("data-interval") || '5000';
                    return old_interval === interval;
                })
                .addClass("active");
        },

        /**
         * Open domain selector dialog
         * @returns {Promise}
         */
        select_domain: function () {
            var self = this;
            var def = wUtils.prompt({
                id: this.popup_template_id,
                window_title: this.popup_title,
                input: _t("Domain (can be empty)"),
                init: function () {
                    return self.$target.attr("data-domain");
                },
            });
            return def.always(function (domain) {
                var sdomain = domain || '';
                self.$target.attr("data-domain", sdomain.replace(/'/g, '"'));
                self._refreshAnimations();
                // The change is made after the option selection, so we
                // need send a new "option change" to make sure the new
                // changes are saved.
                self.__click = true;
                self._select(false, self.$target);
                self.$target.trigger('snippet-option-change', [self]);
            });
        },

        /**
         * @override
         */
        cleanForSave: function () {
            this._super.apply(this, arguments);
            this.$target.empty();
        },

        /**
         * @override
         */
        interval: function (previewMode, value) {
            this.$target.find('.carousel:first')
                .carousel('dispose')
                .carousel({
                    interval: Number(value),
                });
        },
    });
});
