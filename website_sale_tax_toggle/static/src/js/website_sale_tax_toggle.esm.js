/** @odoo-module **/

/* Copyright 2020 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {browser} from "@web/core/browser/browser";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.tax_toggle_button = publicWidget.Widget.extend({
    selector: ".js_tax_toggle_management",
    events: {
        "click .js_tax_toggle_btn": "_onPublishBtnClick",
    },
    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
    },
    async _onPublishBtnClick(ev) {
        ev.preventDefault();
        const $data = $(ev.currentTarget).parents(".js_tax_toggle_management:first");
        const result = await this.rpc($data.data("controller"));
        $data.find("input").prop("checked", result);
        browser.location.reload();
    },
});
