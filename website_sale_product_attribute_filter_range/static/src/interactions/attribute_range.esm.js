/** @odoo-module **/
/* global document, URL, URLSearchParams, window */
// Copyright 2025 EthicHub
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AttributeRangeFilter = publicWidget.Widget.extend({
    selector: ".o_wsale_products_page",
    events: {
        'newRangeValue .o_wsale_attr_range_option input[type="range"]':
            "_onRangeSelected",
    },

    /**
     * Handle range slider value change and redirect with filter params.
     *
     * @private
     * @param {Event} ev
     */
    _onRangeSelected(ev) {
        const range = ev.currentTarget;
        const attrId = range.dataset.attributeId;
        const url = new URL(range.dataset.url || "/shop", window.location.origin);
        const searchParams = url.searchParams;

        // Carry over existing attrib_range params, excluding this attribute.
        const currentParams = new URLSearchParams(window.location.search);
        for (const existing of currentParams.getAll("attrib_range")) {
            if (!existing.startsWith(`${attrId}-`)) {
                searchParams.append("attrib_range", existing);
            }
        }

        // Add new range if not at full extent.
        if (
            parseFloat(range.min) !== range.valueLow ||
            parseFloat(range.max) !== range.valueHigh
        ) {
            searchParams.append(
                "attrib_range",
                `${attrId}-${range.valueLow}-${range.valueHigh}`
            );
        }

        const productList = document.querySelector(
            ".o_wsale_products_grid_table_wrapper"
        );
        if (productList) {
            productList.classList.add("opacity-50");
        }
        window.location = `${url.pathname}?${searchParams.toString()}`;
    },
});

export default publicWidget.registry.AttributeRangeFilter;
