odoo.define("website_sale_custom_filter.price_range_option", function (require) {
    "use strict";

    const publicWidget = require("web.public.widget");

    publicWidget.registry.CustomFilterCollapse = publicWidget.Widget.extend({
        selector: "#wsale_products_custom_filters",
        events: {
            "click .fa-chevron-right": "_onOpenClick",
            "click .fa-chevron-down": "_onCloseClick",
        },

        // --------------------------------------------------------------------------
        // Handlers
        // --------------------------------------------------------------------------

        /**
         * @private
         * @param {Event} ev
         */
        _onOpenClick: function (ev) {
            var $fa = $(ev.currentTarget);
            $fa.parents("li").children()[1].style.display = "inline-block";
            $fa.toggleClass("fa-chevron-down fa-chevron-right");
        },
        /**
         * @private
         * @param {Event} ev
         */
        _onCloseClick: function (ev) {
            var $fa = $(ev.currentTarget);
            $fa.parents("li").children()[1].style.display = "none";
            $fa.toggleClass("fa-chevron-right fa-chevron-down");
        },
    });

    publicWidget.registry.CheckboxCustomFilterSelector = publicWidget.Widget.extend({
        selector: "#wsale_products_custom_filters",
        events: {
            'change input[type="checkbox"]': "_onChangeCustomAttribute",
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onChangeCustomAttribute(ev) {
            const search = $.deparam(window.location.search.substring(1));

            if (ev.currentTarget.checked) {
                if (search.cust_filter) {
                    search.cust_filter += "&" + ev.currentTarget.id;
                } else {
                    search.cust_filter = ev.currentTarget.id;
                }
            } else {
                search.cust_filter = search.cust_filter.replace(
                    ev.currentTarget.id,
                    ""
                );
            }
            window.location.search = $.param(search);
        },
    });

    publicWidget.registry.CheckboxCustomRadioSelector = publicWidget.Widget.extend({
        selector: "#wsale_products_custom_filters",
        events: {
            'change input[type="radio"]': "_onChangeCustomColorAttribute",
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onChangeCustomColorAttribute(ev) {
            const search = $.deparam(window.location.search.substring(1));

            if (ev.currentTarget.checked) {
                if (search.cust_filter) {
                    search.cust_filter += "&" + ev.currentTarget.id;
                } else {
                    search.cust_filter = ev.currentTarget.id;
                }
            } else {
                search.cust_filter = search.cust_filter.replace(
                    ev.currentTarget.id,
                    ""
                );
            }
            window.location.search = $.param(search);
        },
    });

    publicWidget.registry.multirangCustomFilterSelector = publicWidget.Widget.extend({
        selector: "#wsale_products_custom_filters",
        events: {
            'newRangeValue input[type="range"]': "_onCustomFilterRangeSelected",
        },

        // ----------------------------------------------------------------------
        // Handlers
        // ----------------------------------------------------------------------
        /**
         * @private
         * @param {Event} ev
         */
        _onCustomFilterRangeSelected(ev) {
            const range = ev.currentTarget;
            const search = $.deparam(window.location.search.substring(1));
            const re = new RegExp(`${range.id}` + "_\\d+(.\\d+)?");

            if (parseFloat(range.min) !== range.valueLow) {
                if (search.min_cust_filter) {
                    if (search.min_cust_filter.includes(range.id)) {
                        // If there is already filter id in search, find & replace it with new value
                        search.min_cust_filter = search.min_cust_filter.replace(
                            re,
                            range.id + "_" + range.valueLow
                        );
                    } else {
                        search.min_cust_filter += "," + range.id + "_" + range.valueLow;
                    }
                } else {
                    search.min_cust_filter = range.id + "_" + range.valueLow;
                }
            } else if (search.min_cust_filter) {
                search.min_cust_filter = search.min_cust_filter.replace(re, "");
            }
            if (parseFloat(range.max) !== range.valueHigh) {
                if (search.max_cust_filter) {
                    if (search.max_cust_filter.includes(range.id)) {
                        // If there is already filter id in search, find & replace it with new value
                        search.max_cust_filter = search.max_cust_filter.replace(
                            re,
                            range.id + "_" + range.valueHigh
                        );
                    } else {
                        search.max_cust_filter +=
                            "," + range.id + "_" + range.valueHigh;
                    }
                } else {
                    search.max_cust_filter = range.id + "_" + range.valueHigh;
                }
            } else if (search.max_cust_filter) {
                search.max_cust_filter = search.max_cust_filter.replace(re, "");
            }
            window.location.search = $.param(search);
        },
    });
});
