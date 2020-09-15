// Copyright 2020 Tecnativa - Alexandre Díaz
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
odoo.define("website_sale_attribute_filter_price.Shop", function (require) {
    "use strict";

    var sAnimation = require("website.content.snippets.animation");

    sAnimation.registry.js_attribute_filter_price = sAnimation.Class.extend({
        selector: ".js_attribute_filter_price",

        /**
         * @override
         */
        start: function () {
            this.$price_slider = this.$target.find("#filter_price_slider");
            this.$min_value_input = this.$target.find("#price_range_min_value");
            this.$max_value_input = this.$target.find("#price_range_max_value");
            this.$clean_btn = this.$target.find("#clear_price_filter");
            this.$price_slider.on("change", this._onChangeSlider.bind(this));
            this._createSlider();
            this.$min_value_input.on("change", this._onChangeMinValue.bind(this));
            this.$max_value_input.on("change", this._onChangeMaxValue.bind(this));
            this.$clean_btn.on("click", this._onClickClear.bind(this));
            return this._super.apply(this, arguments);
        },
        /**
         * @override
         */
        destroy: function () {
            this.$clean_btn.off("click");
            this.$min_value_input.off("change");
            this.$max_value_input.off("change");
            this.$price_slider.off("change");
            this.$price_slider.destroy();
            this._super.apply(this, arguments);
        },

        _getSliderOptions: function () {
            var options = this.$price_slider.data("options") || {};
            return _.extend({
                hide_min_max: true,
                keyboard: true,
                min: 0,
                max: this.$price_slider.data("max_price"),
                from: this.$price_slider.data("custom_min_price"),
                to: this.$price_slider.data("custom_max_price"),
                prefix: this.$price_slider.data("symbol"),
                type: "double",
                step: 1,
                grid: false,

                onChange: this._onChangeCustomSlider.bind(this),
            }, options);
        },

        _createSlider: function () {
            this.$price_slider.ionRangeSlider(this._getSliderOptions());
        },

        // Handle Events
        /**
         * Native event
         * @param {ChangeEvent} ev
         */
        _onChangeSlider: function (ev) {
            ev.stopPropagation();
        },
        /**
         * Library event
         * @param {Object} data
         */
        _onChangeCustomSlider: function (data) {
            this.$min_value_input.val(data.from);
            this.$max_value_input.val(data.to);
        },
        _onChangeMinValue: function (ev) {
            ev.stopPropagation();
            var ionRange = this.$price_slider.data("ionRangeSlider");
            ionRange.update({from: $(ev.target).val() || 0});
        },
        _onChangeMaxValue: function (ev) {
            ev.stopPropagation();
            var ionRange = this.$price_slider.data("ionRangeSlider");
            ionRange.update({
                to: $(ev.target).val() || this.$price_slider.data("max_price")
            });
        },
        _onClickClear: function () {
            this.$min_value_input.val('').trigger('change');
            this.$max_value_input.val('').trigger('change');
            this.$price_slider.closest('form').submit();
        }
    });

});
