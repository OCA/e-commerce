// Copyright 2020 Tecnativa - Alexandre Díaz
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
odoo.define("website_sale_attribute_filter_price.Shop", function (require) {
    "use strict";

    require("web.dom_ready");

    $(function () {
        // Price Filter
        const $price_slider = $("#filter_price_slider");
        const $min_value_input = $("#price_range_min_value");
        const $max_value_input = $("#price_range_max_value");
        const $clean_btn = $("#clear_price_filter");
        $price_slider.on("change", (ev) => ev.stopPropagation());
        $price_slider.ionRangeSlider({
            hide_min_max: true,
            keyboard: true,
            min: 0,
            max: $price_slider.data("max_price"),
            from: $price_slider.data("custom_min_price"),
            to: $price_slider.data("custom_max_price"),
            prefix: $price_slider.data("symbol"),
            type: "double",
            step: 1,
            grid: false,
            extra_classes: "irs-primary",

            onChange: function (data) {
                $min_value_input.val(data.from);
                $max_value_input.val(data.to);
            },
        });
        $min_value_input.on("change", function (ev) {
            ev.stopPropagation();
            const ionRange = $price_slider.data("ionRangeSlider");
            ionRange.update({from: $(this).val() || 0});
        });
        $max_value_input.on("change", function (ev) {
            ev.stopPropagation();
            const ionRange = $price_slider.data("ionRangeSlider");
            ionRange.update({
                to: $(this).val() || $price_slider.data("max_price"),
            });
        });

        $clean_btn.on("click", function () {
            $min_value_input.val("").trigger("change");
            $max_value_input.val("").trigger("change");
            $price_slider.closest("form").submit();
        });
    });
});
