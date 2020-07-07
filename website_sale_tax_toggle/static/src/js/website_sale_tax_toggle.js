/* Copyright 2020 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_tax_toggle.tax_toggle_button", function (require) {
    "use strict";

    var sAnimation = require("website.content.snippets.animation");

    sAnimation.registry.tax_toggle_button = sAnimation.Class.extend({
        selector: ".js_tax_toggle_management",
        events: {
            'click .js_tax_toggle_btn': '_onPublishBtnClick',
        },
        _onPublishBtnClick: function (ev) {
            ev.preventDefault();
            var self = this;
            var $data = $(ev.currentTarget).parents(".js_tax_toggle_management:first");
            this._rpc({
                route: $data.data('controller'),
            })
            .done(function (result) {
                $data.find('input').prop("checked", result);
                window.location.reload();
            });
        },
    });

});
