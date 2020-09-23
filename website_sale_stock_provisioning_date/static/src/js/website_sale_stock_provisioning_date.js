/* Copyright 2020 Tecnativa - Ernesto Tejeda
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
odoo.define('website_sale_stock_provisioning_date.load', function (require) {
    'use strict';
    var ajax = require('web.ajax');
    var core = require('web.core');
    var QWeb = core.qweb;
    var load_xml = ajax.loadXML(
        '/website_sale_stock_provisioning_date/static/src/xml/website_sale_stock_product_availability.xml',
         QWeb
    );
    load_xml.then(function() {
        $('.oe_website_sale').find('input[name="add_qty"]').trigger('change');
    });
});
