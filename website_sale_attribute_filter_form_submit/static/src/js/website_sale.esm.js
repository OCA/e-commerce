// Copyright 2021 Tecnativa - David Vidal
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import publicWidget from "@web/legacy/js/public/public_widget";
import sAnimation from "@website/js/content/snippets.animation";

sAnimation.registry.WebsiteSale.include({
    read_events: {
        ...sAnimation.registry.WebsiteSale.prototype.read_events,
        "change .css_attribute_color input": "_onChangeColorAttribute",
    },
    /**
     * Highlight selected color as we prevent form submit we need to have
     * a visual feedback on color change.
     *
     * @private
     * @param {MouseEvent} ev
     */
    _onChangeColorAttribute: function (ev) {
        const $parent = $(ev.target).closest(".js_attributes");
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
        const manual = $(ev.target).closest(".js_attributes_manual");
        if (!manual.length) {
            this._super.apply(this, arguments);
        }
    },
});

publicWidget.registry.websiteSaleOffcanvas.include({
    events: {
        ...publicWidget.registry.websiteSaleOffcanvas.prototype.events,
        "click button[name='btn_submit_filters_mobile']":
            "_clickBtnSubmitFiltersMobile",
    },
    _clickBtnSubmitFiltersMobile: function () {
        this.$el.find("form").submit();
    },
});
