// Copyright 2020 Tecnativa - Alexandre Díaz
// License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
odoo.define("website_snippet_carousel_product.snippet_options", function(require) {
    "use strict";

    const core = require("web.core");
    const options = require("web_editor.snippets.options");
    const wUtils = require("website.utils");

    const _t = core._t;

    options.registry.js_product_carousel = options.Class.extend({
        popup_template_id: "editor_new_product_carousel_domain",
        popup_title: _t("Add a products carousel"),

        /**
         * @override
         */
        _onLinkClick: function(ev) {
            // Get the selected menu item
            const $elm = $(ev.target);
            if ($elm.is(".s_carousel_set_domain")) {
                ev.stopImmediatePropagation();
                this.select_domain();
            } else if ($elm.is("[data-products-per-slide]")) {
                this.$target.attr(
                    "data-products-per-slide",
                    $elm.attr("data-products-per-slide")
                );
                this._refreshPublicWidgets();
            } else if ($elm.is("[data-products-limit]")) {
                this.$target.attr(
                    "data-products-limit",
                    $elm.attr("data-products-limit")
                );
                this._refreshPublicWidgets();
            } else if ($elm.is("[data-interval]")) {
                this.$target.attr("data-interval", $elm.attr("data-interval"));
                this._refreshPublicWidgets();
            }
            return this._super.apply(this, arguments);
        },

        /**
         * @override
         */
        onBuilt: function() {
            this._super();
            this.select_domain();
        },

        /**
         * @override
         */
        _setActive: function() {
            const _this = this;
            this._super.apply(this, arguments);
            // Active 'Limit' option
            this.$el
                .find("[data-products-limit]")
                .addBack("[data-products-limit]")
                .removeClass("active")
                .filter(function() {
                    const limit = $(this).attr("data-products-limit");
                    const old_limit = _this.$target.attr("data-products-limit") || "12";
                    return old_limit === limit;
                })
                .addClass("active");
            // Active 'Show' option
            this.$el
                .find("[data-products-per-slide]")
                .addBack("[data-products-per-slide]")
                .removeClass("active")
                .filter(function() {
                    const pps = $(this).attr("data-products-per-slide");
                    const old_pps =
                        _this.$target.attr("data-products-per-slide") || "4";
                    return old_pps === pps;
                })
                .addClass("active");
            // Active 'Interval' option
            this.$el
                .find("[data-interval]")
                .addBack("[data-interval]")
                .removeClass("active")
                .filter(function() {
                    const interval = $(this).attr("data-interval");
                    const old_interval = _this.$target.attr("data-interval") || "5000";
                    return old_interval === interval;
                })
                .addClass("active");
        },

        /**
         * Open domain selector dialog
         * @returns {Promise}
         */
        select_domain: function() {
            const _this = this;
            return wUtils
                .prompt({
                    id: this.popup_template_id,
                    window_title: this.popup_title,
                    input: _t("Domain (can be empty)"),
                    init: function() {
                        return _this.$target.attr("data-domain");
                    },
                })
                .then(domain => this.set_domain(domain.val))
                .catch(() => this.set_domain());
        },

        /**
         * @param {String} domain
         */
        set_domain: function(domain) {
            const sdomain = domain || "";
            this.$target.attr("data-domain", sdomain.replace(/'/g, '"'));
            this._refreshPublicWidgets();
            // The change is made after the option selection, so we
            // need send a new "option change" to make sure the new
            // changes are saved.
            this.__click = true;
            this._select(false, this.$target);
            this.$target.trigger("snippet-option-change", [this]);
        },

        /**
         * @override
         */
        cleanForSave: function() {
            this._super.apply(this, arguments);
            this.$target.empty();
        },

        /**
         * @override
         */
        interval: function(previewMode, value) {
            this.$target
                .find(".carousel:first")
                .carousel("dispose")
                .carousel({
                    interval: Number(value),
                });
        },
    });
});
