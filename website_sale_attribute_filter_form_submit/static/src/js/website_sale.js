// Copyright 2021 Tecnativa - David Vidal
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
odoo.define("website_sale_attribute_filter_form_submit.website_sale", function (
    require
) {
    "use strict";

    var sAnimations = require("website.content.snippets.animation");

    sAnimations.registry.WebsiteSale.include({
        read_events: _.extend(
            {
                "change .css_attribute_color input": "_onChangeColorAttribute",
            },
            sAnimations.registry.WebsiteSale.prototype.read_events
        ),
        /**
         * Highlight selected color as we prevent form submit we need to have
         * a visual feedback on color change.
         *
         * @private
         * @param {MouseEvent} ev
         */
        _onChangeColorAttribute: function (ev) {
            var $parent = $(ev.target).closest(".js_attributes");
            $parent
                .find(".css_attribute_color")
                .removeClass("active")
                .filter(":has(input:checked)")
                .addClass("active");
        },
        /**
         * When the view is active, we deactivate the auto submit
         *
         * @private
         * @param {MouseEvent} ev
         */
        _onChangeAttribute: function (ev) {
            var manual = $(ev.target).closest(".js_attributes_manual");
            if (manual.length) {
                return true;
            }
            this._super.apply(this, arguments);
        },
    });
});
