odoo.define("website_sale_change_payment_fee.checkout", function(require) {
    "use strict";

    require("web.dom_ready");
    require("web.core");
    var ajax = require("web.ajax");
    var concurrency = require("web.concurrency");
    var dp = new concurrency.DropPrevious();

    var _onUpdatePaymentFee = function(result) {
        var $pay_button = $("#o_payment_form_pay");
        var $amount_payment_fee = $("#order_payment_fee span.oe_currency_value");
        var $amount_untaxed = $("#order_total_untaxed span.oe_currency_value");
        var $amount_tax = $("#order_total_taxes span.oe_currency_value");
        var $amount_total = $("#order_total span.oe_currency_value");
        var $discount = $("#order_discounted");

        if ($discount && result.new_amount_order_discounted) {
            // Cross module without bridge
            // Update discount of the order
            $discount
                .find(".oe_currency_value")
                .text(result.new_amount_order_discounted);
        }

        if (result.status === true) {
            $amount_payment_fee.text(result.amount_payment_fee);
            $amount_untaxed.text(result.new_amount_untaxed);
            $amount_tax.text(result.new_amount_tax);
            $amount_total.text(result.new_amount_total);
            $pay_button.data("disabled_reasons").carrier_selection = false;
            $pay_button.prop(
                "disabled",
                _.contains($pay_button.data("disabled_reasons"), true)
            );
        } else {
            console.error(result.error_message);
            $amount_payment_fee.text(result.amount_payment_fee);
            $amount_untaxed.text(result.new_amount_untaxed);
            $amount_tax.text(result.new_amount_tax);
            $amount_total.text(result.new_amount_total);
        }
    };

    var $amount_delivery = $("#order_delivery span.oe_currency_value");
    $amount_delivery.on("DOMSubtreeModified", function() {
        var selected_acquirer = $('input[name="pm_id"][checked="True"]')[0].value;
        if (selected_acquirer.includes("_") === true) {
            // Extract acquirer id simply from the input value, e.g. form_5
            var acquirer_id = selected_acquirer.split("_")[1];
        } else {
            // When saved token <input> is selected, the value is the id of
            // the payment token, we need to search the acquirer id by
            // data-provider attribute in the input, e.g. data-provider='stripe'
            var acquirer_id = $(
                "input[data-provider=" + $(this).attr("data-provider") + "]"
            )[0].value.split("_")[1];
        }
        var values = {acquirer_id: acquirer_id};
        dp.add(ajax.jsonRpc("/shop/update_payment_fee", "call", values)).then(
            _onUpdatePaymentFee
        );
    });
});
