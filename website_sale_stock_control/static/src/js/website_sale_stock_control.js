/* Copyright 2017 Sergio Teruel (http://www.tecnativa.com.com)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_stock_control.website_sale", function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var QWeb = core.qweb;
    var template_ready = $.Deferred();

    QWeb.add_template('/website_sale_stock_control/static/src/xml/website_sale_stock_control_product_availability.xml', function(error){
        if (error){
            template_ready.reject();
        } else {
            template_ready.resolve();
        }
    });

    function allow_buy($html){
        $html.removeClass("css_not_available");
        $html.find("#add_to_cart").removeClass("disabled");
        template_ready.done(function(){
            $html.find("#no_stock").remove();
        });
    };

    function deny_buy($html, product_id){
        $html.addClass("css_not_available");
        $html.find("#add_to_cart").addClass("disabled");
        if (product_id){
            template_ready.done(function(){
                var $message = $(QWeb.render('website_sale_stock_control.no_stock'));
                $html.find(".availability_messages").html($message);
            });
        } else {
            template_ready.done(function(){
                $html.find("#no_stock").remove();
            });
        };
    };

    $(document).ready(function() {
        if(!$('.oe_website_sale').length) {
            return $.Deferred().reject("DOM doesn't contain '#o_shop_collapse_category, .oe_website_sale'");
        }
        $('.oe_website_sale').each(function() {
            var oe_website_sale = this;
            $(oe_website_sale).on('change', 'input.js_variant_change, select.js_variant_change, ul[data-attribute_value_ids]', function (ev) {
                var $ul = $(ev.target).closest('.js_add_cart_variants');
                var $parent = $ul.closest('.js_product');
                var $product_id = $parent.find('.product_id').first();
                var variant_ids = $ul.data("attribute_value_ids");
                var values = [];
                var unchanged_values = $parent.find('div.oe_unchanged_value_ids').data('unchanged_value_ids') || [];
                $parent.find('input.js_variant_change:checked, select.js_variant_change').each(function () {
                    values.push(+$(this).val());
                });
                values =  values.concat(unchanged_values);
                $parent.find("label").removeClass("text-muted css_not_available");
                var product_id = false;
                var no_stock = false;
                for (var k in variant_ids) {
                    if (_.isEmpty(_.difference(variant_ids[k][1], values))) {
                        product_id = variant_ids[k][0];
                        if (variant_ids[k][4] <= 0.0) {
                            no_stock = true;
                        }
                        break;
                    }
                }
                if (product_id) {
                    allow_buy($parent);
                    if (no_stock) {
                        deny_buy($parent,product_id);
                    };
                } else {
                    deny_buy($parent, product_id);
                };
            });
        });
        $('.js_variant_change:checked').trigger('change');
        $('input[name="add_qty"]').trigger('change');
    });
});
