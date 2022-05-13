/* Copyright 2022 Tecnativa - David Vidal
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
odoo.define("website_sale_hide_price.load", function(require) {
    "use strict";
    const ajax = require("web.ajax");
    const core = require("web.core");
    const QWeb = core.qweb;
    ajax.loadXML(
        "/website_sale_hide_price/static/src/xml/website_sale_templates.xml",
        QWeb
    );
});
