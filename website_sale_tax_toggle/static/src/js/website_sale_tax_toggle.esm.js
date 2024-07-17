/** @odoo-module **/

/* Copyright 2020 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {browser} from "@web/core/browser/browser";
import publicWidget from "web.public.widget";

publicWidget.registry.tax_toggle_button = publicWidget.Widget.extend({
    selector: ".js_tax_toggle_management",
    events: {
        "click .js_tax_toggle_btn": "_onPublishBtnClick",
    },
    _onPublishBtnClick: function (ev) {
        ev.preventDefault();
        const $data = $(ev.currentTarget).parents(".js_tax_toggle_management:first");
        this._rpc({
            route: $data.data("controller"),
        }).then(function (result) {
            $data.find("input").prop("checked", result);
            browser.location.reload();
        });
    },
});
