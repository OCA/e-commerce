// Copyright 2021 Studio73 - Miguel Gandia
// License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
odoo.define("website_sale_attribute_filter_range.Shop", function (require) {
    "use strict";

    require("web.dom_ready");

    $(function () {
        const $filter_range_sliders = $(".filter_range_slider");
        function updateFilters($elements, $min_value, $max_value) {
            const min_value = $min_value.val();
            const max_value = $max_value.val();
            $elements.each(function () {
                const value_attr = Number($(this).data("value-attr"));
                $(this).prop(
                    "checked",
                    value_attr >= min_value && value_attr <= max_value
                );
            });
        }
        $filter_range_sliders.each(function () {
            const $el = $(this);
            const $max_value_input = $(`#${$el.data("id")}-range_range_max_value`);
            const $min_value_input = $(`#${$el.data("id")}-range_range_min_value`);
            const $clean_btn = $(`#${$el.data("id")}-clear_range_filter`);
            const $els_attr_value = $(
                `#${$el.data("id")}-input-attr-values-filter input`
            );

            let active_filters = [];
            $els_attr_value.each(function () {
                const value_attr = Number($(this).data("value-attr"));
                if ($(this).is(":checked")) {
                    active_filters.push(value_attr);
                }
            });
            active_filters = active_filters.sort((a, b) => a - b);

            let from = $el.data("custom_min_range");
            let to = $el.data("custom_max_range");
            if (active_filters.length) {
                from = active_filters[0];
                to = active_filters[active_filters.length - 1];
            }
            $min_value_input.val(from);
            $max_value_input.val(to);

            $el.on("change", (ev) => ev.stopPropagation());
            $el.ionRangeSlider({
                hide_min_max: true,
                keyboard: true,
                min: $el.data("min_range"),
                max: $el.data("max_range"),
                from,
                to,
                prefix: $el.data("symbol"),
                type: "double",
                step: 1,
                grid: false,
                extra_classes: "irs-primary",

                onChange: function (data) {
                    console.log(data);
                    $min_value_input.val(data.from);
                    $max_value_input.val(data.to);
                },
                onFinish: function () {
                    updateFilters($els_attr_value, $min_value_input, $max_value_input);
                },
            });
            $min_value_input.on("change", function (ev) {
                ev.stopPropagation();
                const ionRange = $el.data("ionRangeSlider");
                ionRange.update({from: $(this).val() || $el.data("min_range")});
                updateFilters($els_attr_value, $min_value_input, $max_value_input);
            });
            $max_value_input.on("change", function (ev) {
                ev.stopPropagation();
                const ionRange = $el.data("ionRangeSlider");
                ionRange.update({to: $(this).val() || $el.data("max_range")});
                updateFilters($els_attr_value, $min_value_input, $max_value_input);
            });

            $clean_btn.on("click", function () {
                $min_value_input.val($el.data("min_range")).trigger("change");
                $max_value_input.val($el.data("max_range")).trigger("change");
                $el.closest("form").submit();
            });
        });
    });
});
