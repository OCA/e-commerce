odoo.define("website_product_attribute_filter_applied.publicWidget", function (
    require
) {
    "use strict";

    // Website_sale is required so that it loads the widget in the publicWidget registry
    require("website_sale.website_sale_category");
    var publicWidget = require("web.public.widget");

    publicWidget.registry.WebsiteSale.include({
        events: _.extend(publicWidget.registry.WebsiteSale.prototype.events, {
            "click #wsale_products_attributes_filters_applied label":
                "_onChangeAppliedFilterAttribute",
        }),

        /**
         * @private
         * @param {Event} ev
         */
        _onChangeAppliedFilterAttribute: function (ev) {
            if (!ev.isDefaultPrevented()) {
                ev.preventDefault();
                $(ev.currentTarget).parent(".badge").hide();
                var value = $(ev.currentTarget).data("value");
                var js_attributes = $("form.js_attributes");
                var input_elements = [
                    "input[value=" + value + "]",
                    "option[value=" + value + "]",
                ];
                var input = js_attributes.find([input_elements].join(","));
                input.prop("checked", false);
                input.prop("selected", false);
                input.trigger("change");
            }
        },
    });

    return publicWidget;
});
