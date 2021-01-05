odoo.define("website_sale_attribute_filter_multiselect.website_sale", function (
    require
) {
    "use strict";

    var publicWidget = require("web.public.widget");

    require("web.dom_ready");

    publicWidget.registry.WebsiteSale.include({
        start: function () {
            var context = {};
            this.trigger_up("context_get", {
                callback: function (ctx) {
                    context = ctx;
                },
            });
            var def = this._super.apply(this, arguments);
            this.$el.find("select.multiple-select").multipleSelect({
                locale: context.lang.replace("_", "-"),
                filter: true,
                showClear: true,
            });
            return def;
        },

        _onChangeAttribute: function (ev) {
            if (
                !$(ev.currentTarget).hasClass("multiple-select") &&
                $(ev.currentTarget).closest(".ms-drop").length === 0
            ) {
                this._super.apply(this, arguments);
            }
        },
    });
});
