odoo.define("website_sale_stock_available_display.load", function(require) {
    "use strict";
    const ajax = require("web.ajax");
    const core = require("web.core");
    const QWeb = core.qweb;
    ajax.loadXML(
        "/website_sale_stock_available_display/static/src/xml/website_sale_stock_product_availability.xml",
        QWeb
    );
});
