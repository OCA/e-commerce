/* Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
odoo.define("website_sale_custom_info.quick_filter", function (require) {
    "use strict";
    var animation = require("web_editor.snippets.animation");
    var $ = require("$");

    return animation.registry.website_sale_custom_info_quick_filter =
    animation.Class.extend({
        selector: "form.js_website_sale_custom_info_quick_filter",
        start: function () {
            this.$inputs = this.$("input");
            this.$el.on(
                "change",
                "input[type=checkbox]",
                $.proxy(this.submit, this)
            );
            this.$el.on(
                "keyup",
                "input[type=text], input[type=number]",
                $.proxy(this.submit, this)
            );
        },
        keyup: function (event) {
            if (event.key === "Enter") {
                return this.submit();
            }
        },
        submit: function () {
            this.$el.submit();
            this.$inputs.prop("disabled", true);
        },
    });
});
