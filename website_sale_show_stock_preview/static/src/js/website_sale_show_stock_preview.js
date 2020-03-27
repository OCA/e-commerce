odoo.define('website_sale_show_stock_preview.shop_stock', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
var rpc = require('web.rpc');
var session = require('web.session')


publicWidget.registry.WebsiteSaleShowStockPreview = publicWidget.Widget.extend({
    selector: '#products_grid',
    template: 'website_sale_show_stock_preview.test',
    xmlDependencies: ['/website_sale_show_stock_preview/static/src/xml/website_sale_show_stock_preview.xml'],

    start: function () {
        var self = this;
        var def = [this._super.apply(this, arguments)];
        this.render_stock();
        return def;
    },
    render_stock: function(){
        var self = this;
        var products = $(".o_wsale_products_item_title");
        rpc.query({
            model: 'website',
            method: 'search_read',
            domain: [['id', '=', session.website_id]],
            fields: ['warehouse_id']
        }).then(function(result) {
            var warehouse_id = result[0]['warehouse_id'];
            _.extend(session.user_context, {
               'warehouse': warehouse_id[0],
            });
            console.log(session.user_context);
            var product_ids = [];
            _.each(products, function(elem) {
                product_ids.push($(elem).find("a").data("oe-id"));
            });
            self.get_products_stock(product_ids).then( (products_qty) => {
                _.each(products_qty, function(product) {
                    const elem = self.get_element_by_id(product.id)
                    elem.parent().parent().find('.product_price')
                        .append($(core.qweb.render('website_sale_show_stock_preview.test', {
                            virtual_available: product.virtual_available,
                        })).get(0));
                });
            })
        });

    },
    get_products_stock: async function (product_ids) {
        var result = await rpc.query({
            model: 'product.template',
            method: 'search_read',
            args: [[['id', 'in', product_ids]], ['virtual_available']],
            context: session.user_context,
        })
        return result;
    },
    get_element_by_id: function (product_id) {
        return $(`.o_wsale_products_item_title a[data-oe-id='${product_id}']`);
    }
});
})
