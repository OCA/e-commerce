odoo.define('website_sale_stock_available_display.load', function (require) {
    'use strict';
    var ajax = require('web.ajax');
    var core = require('web.core');
    var ProductConfiguratorMixin = require(
        'website_sale_stock.ProductConfiguratorMixin');
    var QWeb = core.qweb;
    var load_xml = ajax.loadXML(
        '/website_sale_stock_available_display/static/src/xml/website_sale_stock_product_availability.xml',
         QWeb
    );
    load_xml.then(function() {
        $('.oe_website_sale').find('input[name="add_qty"]').trigger('change');
    });
});
