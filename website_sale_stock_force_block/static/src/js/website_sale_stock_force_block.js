odoo.define('website_sale_stock_force_block.load', function (require) {
    'use strict';
    var ajax = require('web.ajax');
    var core = require('web.core');
    var sAnimations = require('website.content.snippets.animation');
    var ProductConfiguratorMixin = require('website_sale_stock.ProductConfiguratorMixin');
    var QWeb = core.qweb;
    var load_xml = ajax.loadXML(
        '/website_sale_stock_force_block/static/src/xml/website_sale_stock_force_block.xml',
         QWeb
    );

    // Save original method
    var _onChangeCombinationStock = ProductConfiguratorMixin._onChangeCombinationStock;
    ProductConfiguratorMixin._onChangeCombinationStock = function (ev, $parent, combination) {
        if (!this.isWebsite){
            return;
        }
        if (combination.product_type === 'product' && combination.inventory_availability == 'custom_block') {
            $parent.find('#add_to_cart').addClass('disabled out_of_stock');
            load_xml.then(function () {
                $('.oe_website_sale')
                .find('.availability_message_' + combination.product_template)
                .remove();
                var $message = $(QWeb.render('website_sale_stock.product_availability', combination));
                $('div.availability_messages').html($message);
            });
        }
        else {
            _onChangeCombinationStock.apply(this, arguments);
        }
    };
    return ProductConfiguratorMixin;
});
