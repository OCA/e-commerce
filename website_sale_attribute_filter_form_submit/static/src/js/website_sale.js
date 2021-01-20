odoo.define("website_sale_attribute_filter_form_submit.website_sale", function (
    require
) {
    "use strict";

    var publicWidget = require("web.public.widget");
    require("web.dom_ready");

    publicWidget.registry.WebsiteSale.include({
        _onChangeAttribute: function () {
            return true;
        },
    });
});
