odoo.define('website_sale_one_step_checkout_delivery.delivery', function (require) {

    var ajax = require('web.ajax');
    var base = require('web_editor.base');
    var utils = require('web.utils');
    var core = require('web.core');

    var _t = core._t;

    function price_to_str(price) {
        var l10n = _t.database.parameters;
        var precision = 2;

        if ($(".decimal_precision").length) {
            precision = parseInt($(".decimal_precision").last().data('precision'));
        }
        var formatted = _.str.sprintf('%.' + precision + 'f', price).split('.');
        formatted[0] = utils.insert_thousand_seps(formatted[0]);
        return formatted.join(l10n.decimal_point);
    }

    function changeDelivery(carrierId) {
        ajax.jsonRpc('/shop/checkout/change_delivery', 'call', {'carrier_id': carrierId})
            .then(function (result) {
                if (result) {
                    if (result.success) {
                        if (result.order_total) {
                            $('#order_total .oe_currency_value').text(price_to_str(result.order_total));
                            $('.js_payment input[name=amount]').val(price_to_str(result.order_total));
                        }
                        if (result.order_total_taxes || result.order_total_delivery === 0) {
                            $('#order_total_taxes .oe_currency_value').text(price_to_str(result.order_total_taxes));
                        }
                        if (result.order_total_delivery || result.order_total_delivery === 0) {
                            $('#order_delivery .oe_currency_value').text(price_to_str(result.order_total_delivery));
                        }
                    } else if (result.errors) {
                        // ???
                    }
                } else {
                    // ???
                    window.location.href = '/shop';
                }
            });
    }

    base.dom_ready.done(function () {
        // when choosing a delivery carrier, update the total prices
        // original part in website_sale_delivery.js uses `delivery_carrier`
        // since we don't want that JS triggered, we're using our own id `delivery_carrier_osc
        // to avoid the page reload of the original one
        var $carrier = $('#delivery_carrier_osc');
        $carrier.find('input[name="delivery_type"]').click(function (ev) {
        var carrierId = $(ev.currentTarget).val();
        changeDelivery(carrierId);
        });
    });
});