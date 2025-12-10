/* Copyright 2025 Tecnativa - Pilar Vargas
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.ShippingHideHeaderFooter = publicWidget.Widget.extend({
    selector: "#portal-session-flags",
    start: function () {
        var def = this._super.apply(this, arguments);
        const hasPortalSession =
            $("#portal-session-flags").data("hasPortalSession") === 1;
        if (hasPortalSession) {
            $("header").hide();
            $("#footer").hide();
        }
        return def;
    },
});
