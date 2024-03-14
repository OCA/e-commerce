odoo.define("website_sale_infinite_scroll.website", function (require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    publicWidget.registry.WebsiteSaleBacktoTop = publicWidget.Widget.extend({
        selector: ".oe_website_sale",
        events: {
            "click .btn-back-to-top": "_onClickBacktoTop",
        },
        _onClickBacktoTop: function (event) {
            event.preventDefault();
            const $element = $(event.currentTarget);
            $element.addClass("d-none");
        },
    });
});
